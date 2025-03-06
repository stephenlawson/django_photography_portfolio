# photo_app/management/commands/create_cherry_slots.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, datetime, timedelta
import random
from ...models import CherryBlossomSession

class Command(BaseCommand):
    help = 'Create Cherry Blossom session time slots for a date range with all slots visible but some marked as booked'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str, help='Start date (YYYY-MM-DD)')
        parser.add_argument('end_date', type=str, help='End date (YYYY-MM-DD)')
        parser.add_argument('--keep-existing', action='store_true', help='Keep existing slots')
        parser.add_argument('--reset-all', action='store_true', help='Reset ALL cherry blossom sessions (not just date range)')
        parser.add_argument('--weekend-density', type=float, default=0.4, help='Percentage of weekend slots to be available (default: 0.4)')
        parser.add_argument('--weekday-density', type=float, default=0.6, help='Percentage of weekday slots to be available (default: 0.6)')

    def handle(self, *args, **options):
        start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
        weekend_density = options['weekend_density']
        weekday_density = options['weekday_density']
        
        # Reset logic
        if options['reset_all']:
            # Clear ALL cherry blossom sessions, regardless of date
            count = CherryBlossomSession.objects.all().count()
            CherryBlossomSession.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Reset ALL cherry blossom sessions ({count} deleted)'))
        elif not options['keep_existing']:
            # Clear sessions in the specified date range (default behavior)
            count = CherryBlossomSession.objects.filter(date__range=[start_date, end_date]).count()
            CherryBlossomSession.objects.filter(date__range=[start_date, end_date]).delete()
            self.stdout.write(self.style.SUCCESS(f'Cleared existing slots for selected date range ({count} deleted)'))
        
        # Array to store all created sessions
        all_sessions = []
        current_date = start_date

        # Fixed end time for all sessions (7:30 PM maximum)
        def get_latest_end_time():
            return time(19, 30)  # 7:30 PM maximum end time
        
        # Latest start time would be 7:00 PM for a 30-minute session
        def get_latest_start_time():
            return time(19, 0)  # 7:00 PM
        
        # Function to determine if a time is in golden hour
        def is_golden_hour(session_time):
            # Convert times to datetime for comparison
            session_dt = datetime.combine(datetime.today(), session_time)
            end_dt = datetime.combine(datetime.today(), get_latest_end_time())
            
            # Golden hour is roughly the last hour before end time
            golden_start = end_dt - timedelta(hours=1, minutes=30)
            
            # Return true if session starts during golden hour
            return session_dt >= golden_start

        # Create all sessions first
        while current_date <= end_date:
            # Get end time (7:30 PM fixed maximum)
            end_time = get_latest_end_time()
            latest_start = get_latest_start_time()
            
            is_weekend = current_date.weekday() >= 5  # Saturday = 5, Sunday = 6
            
            # Weekend schedule (all day)
            if is_weekend:
                start = time(8, 0)   # 8:00 AM
            # Weekday schedule (afternoon/evening only)
            else:
                start = time(16, 0)  # 4:00 PM
            
            # Create slots for this day
            self.stdout.write(f"Creating slots for {current_date} from {start} to {end_time}")
            
            # Start time for first session
            current_time = start
            
            while True:
                # Calculate end time for this slot (30 mins later)
                session_end_dt = datetime.combine(current_date, current_time) + timedelta(minutes=30)
                session_end = session_end_dt.time()
                
                # Calculate start time for next slot (adding 5 min break)
                next_session_dt = session_end_dt + timedelta(minutes=5)
                next_session = next_session_dt.time()
                
                # If this session starts before or at our latest start time and ends before or at 7:30 PM
                if current_time <= latest_start and session_end <= end_time:
                    # Check if this time is in golden hour
                    golden_hour_session = is_golden_hour(current_time)
                    
                    # Store session info with default is_booked=False
                    all_sessions.append({
                        'date': current_date,
                        'start_time': current_time,
                        'end_time': session_end,
                        'is_weekend': is_weekend,
                        'is_golden_hour': golden_hour_session,
                        'is_booked': False  # Default to not booked
                    })
                    
                    # Move to next slot
                    current_time = next_session
                else:
                    # We've reached the latest start/end time for today
                    break
            
            current_date += timedelta(days=1)
        
        # Mark sessions as reserved/booked based on density parameters
        # Group sessions by date
        sessions_by_date = {}
        for session in all_sessions:
            date_key = session['date']
            if date_key not in sessions_by_date:
                sessions_by_date[date_key] = []
            sessions_by_date[date_key].append(session)
        
        # Process each date
        for date, day_sessions in sessions_by_date.items():
            # Split into golden hour and non-golden hour sessions
            golden_sessions = [s for s in day_sessions if s['is_golden_hour']]
            regular_sessions = [s for s in day_sessions if not s['is_golden_hour']]
            
            # Keep all golden hour sessions available (is_booked=False)
            
            # Randomly mark non-golden hour sessions as booked based on density
            is_weekend = day_sessions[0]['is_weekend']
            density = weekend_density if is_weekend else weekday_density
            
            # Calculate how many to keep available
            available_count = max(1, int(len(regular_sessions) * density))
            
            # Default to marking all regular sessions as booked
            for session in regular_sessions:
                session['is_booked'] = True
            
            # Randomly select sessions to be available
            if available_count < len(regular_sessions):
                # Randomly select sessions to mark as available
                available_sessions = random.sample(regular_sessions, available_count)
                for session in available_sessions:
                    session['is_booked'] = False  # Mark as available
            else:
                # If we want more than we have, keep all available
                for session in regular_sessions:
                    session['is_booked'] = False
        
        # Now create all sessions in the database
        booked_count = 0
        available_count = 0
        
        for session in all_sessions:
            CherryBlossomSession.objects.create(
                date=session['date'],
                start_time=session['start_time'],
                end_time=session['end_time'],
                duration=30,
                price=125.00,
                location="Brown's Island, Richmond, Virginia",
                is_booked=session['is_booked']
            )
            
            if session['is_booked']:
                booked_count += 1
            else:
                available_count += 1
        
        # Report results
        self.stdout.write(
            self.style.SUCCESS(
                f'Created {len(all_sessions)} total sessions from {start_date} to {end_date}'
            )
        )
        
        # Report available vs reserved counts
        self.stdout.write(
            self.style.SUCCESS(
                f'Sessions breakdown: {available_count} available, {booked_count} reserved/crossed-out'
            )
        )
        
        # Report weekend vs weekday counts
        weekend_count = sum(1 for s in all_sessions if s['is_weekend'])
        weekday_count = len(all_sessions) - weekend_count
        golden_count = sum(1 for s in all_sessions if s['is_golden_hour'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Schedule breakdown: {weekend_count} weekend, {weekday_count} weekday, '
                f'{golden_count} golden hour sessions'
            )
        )