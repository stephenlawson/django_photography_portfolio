# yourapp/management/commands/run_tests.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
import subprocess
from django.conf import settings
import os
import psutil
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


class Command(BaseCommand):
    help = "Run Django tests and Apache Benchmark"

    def handle(self, *args, **options):

        python_path = "/home/taylor1038/python_programs-main/Personal_Projects/django/djangoenv/bin/python3.10"

        django_project_directory = "/home/taylor1038/python_programs-main/Personal_Projects/django/django_portfolio/"
        os.chdir(django_project_directory)
        # Run Django tests
        django_test_process = subprocess.run(
            [python_path, "manage.py", "test"], capture_output=True, text=True
        )
        django_test_output = f"STDOUT:\n{django_test_process.stdout}\n\nSTDERR:\n{django_test_process.stderr}"

        # Run Apache Benchmark
        apache_benchmark_output = subprocess.run(
            ["ab", "-n", "100", "-c", "10", "https://stephen.photography/"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        print(datetime.now())
        print(apache_benchmark_output)
        print(type(apache_benchmark_output))
        str(apache_benchmark_output)
        # Extracting information using regular expressions
        time_taken = re.search(
            r"Time taken for tests:\s+([\d.]+)\s+seconds", apache_benchmark_output
        ).group(1)
        complete_requests = re.search(
            r"Complete requests:\s+(\d+)", apache_benchmark_output
        ).group(1)
        failed_requests = re.search(
            r"Failed requests:\s+(\d+)", apache_benchmark_output
        ).group(1)

        time_per_request_mean = re.search(
            r"Time per request:\s+([\d.]+)\s+\[ms\]\s+\(mean\)", apache_benchmark_output
        ).group(1)
        time_per_request_across_all = re.search(
            r"Time per request:\s+([\d.]+)\s+\[ms\]\s+\(mean, across all concurrent requests\)",
            apache_benchmark_output,
        ).group(1)

        percentage_requests_served = re.findall(
            r"(\d+)%\s+(\d+)", apache_benchmark_output
        )

        # Create a docstring
        apache_benchmark_output_str = f"""</br>
        Time taken for tests: {time_taken} seconds</br>
        Complete requests: {complete_requests}</br>
        Failed requests: {failed_requests}</br>
        Time per request (mean): {time_per_request_mean} ms</br>
        Time per request (mean, across all concurrent requests): {time_per_request_across_all} ms</br>
        Percentage of the requests served within a certain time (ms):</br>
        50% {percentage_requests_served[0][1]}</br>
        66% {percentage_requests_served[1][1]}</br>
        75% {percentage_requests_served[2][1]}</br>
        80% {percentage_requests_served[3][1]}</br>
        90% {percentage_requests_served[4][1]}</br>
        95% {percentage_requests_served[5][1]}</br>
        98% {percentage_requests_served[6][1]}</br>
        99% {percentage_requests_served[7][1]}</br>
        100% {percentage_requests_served[8][1]} (longest request)
        """
        print(apache_benchmark_output_str)

        # Get the path to the bash script in the same directory
        script_path = os.path.join(os.path.dirname(__file__), "check_broken_links.sh")

        # Run the modified bash script
        bash_script_output = subprocess.run(
            ["bash", script_path], capture_output=True, text=True
        )

        # Run sudo certbot certificates
        certbot_output = subprocess.run(
            ["sudo", "/usr/bin/certbot", "certificates"],
            capture_output=True,
            text=True,
            check=True,
        )
        certbot_output = str(certbot_output)
        pattern = r"Expiry Date: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\+\d{2}:\d{2} \(VALID: (\d+) days\)"
        match = re.search(pattern, certbot_output)
        expiry_date = match.group(1)
        validity_days = match.group(2)

        # Format the expiry date to day month year
        expiry_date_formatted = datetime.strptime(
            expiry_date, "%Y-%m-%d %H:%M:%S"
        ).strftime("%d %B %Y")

        # Print the results
        certbot_output_final = (
            f"Expires in {validity_days} days on {expiry_date_formatted}"
        )

        # Get resource utilization summary
        cpu_usage_percent = psutil.cpu_percent(interval=1)
        memory_usage_percent = psutil.virtual_memory().percent

        # Run safety check
        safety_output = subprocess.run(
            [
                "/home/taylor1038/python_programs-main/Personal_Projects/django/djangoenv/bin/safety",
                "check",
                "--short-report",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        if "No known security vulnerabilities reported" in str(safety_output):
            # If present, set safety_output to "No known security vulnerabilities reported."
            safety_output = "No known security vulnerabilities reported."
        else:
            safety_output = safety_output

        # SEO Health Checks
        seo_health_message = self.check_seo_health()

        # Send email with the results
        subject = "Daily Test Results"
        message = (
            f"<b>Django Test Output:</b>\n{django_test_output}\n\n"
            "\n#######################################\n"
            f"<b>Apache Benchmark Output:</b>\n{apache_benchmark_output_str}\n\n"
            "\n#######################################\n"
            f"<b>Bash Script Output:</b>\n{bash_script_output.stdout}"
            "\n#######################################\n"
            f"<b>Certbot Certificates Output:</b>\n{certbot_output_final}"
            "\n#######################################\n"
            f"<b>Resource Utilization Summary:</b>\nCPU Usage: {cpu_usage_percent}%\nMemory Usage: {memory_usage_percent}%"
            "\n#######################################\n"
            f"<b>SEO Health Checks:</b>\n{seo_health_message}"
            "\n#######################################\n"
        )

        html_message = (
            f"<b>Django Test Output:</b><br>{django_test_output}<br><br>"
            "\n#######################################<br>"
            f"<b>Apache Benchmark Output:</b><br>{apache_benchmark_output_str}<br><br>"
            "\n#######################################<br>"
            f"<b>Bash Script Output:</b><br>{bash_script_output.stdout}<br>"
            "\n#######################################<br>"
            f"<b>Certbot Certificates Output:</b><br>{certbot_output_final}<br>"
            "\n#######################################<br>"
            f"<b>Resource Utilization Summary:</b><br>CPU Usage: {cpu_usage_percent}%<br>Memory Usage: {memory_usage_percent}%<br>"
            "\n#######################################<br>"
            f"<b>Safety Check:</b><br>{safety_output}<br>"
            "\n#######################################<br>"
            f"<b>SEO Health Checks:</b><br>{seo_health_message}<br>"
            "\n#######################################<br>"
        )

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            html_message=html_message,
        )

    def check_seo_health(self):
        url = "https://stephen.photography/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Check for the presence of important SEO tags
        title_tag = soup.find("title")
        meta_description_tag = soup.find("meta", {"name": "description"})
        h1_tags = soup.find_all("h1")

        seo_health_message = (
            f"Title Tag: {'Present' if title_tag else 'Not Present'}\n</br>"
            f"Meta Description Tag: {'Present' if meta_description_tag else 'Not Present'}\n</br>"
            f"H1 Tags: {len(h1_tags)} found</br>"
        )

        return seo_health_message
