# seo_content/loader.py
import yaml
from pathlib import Path
from django.core.cache import cache
from django.conf import settings


class SEOLoader:
    _instance = None
    CACHE_KEY = "seo_content_cache"
    CACHE_TIMEOUT = 3600  # 1 hour

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_content()
        return cls._instance

    def _load_content(self):
        """Load all YAML files from seo_content directory with caching"""
        if settings.DEBUG:
            self._content = self._read_yaml_files()
        else:
            self._content = cache.get(self.CACHE_KEY)
            if not self._content:
                self._content = self._read_yaml_files()
                cache.set(self.CACHE_KEY, self._content, self.CACHE_TIMEOUT)

    def _read_yaml_files(self):
        """Read and parse all YAML files"""
        content = {}
        seo_dir = Path(__file__).parent
        print("\nReading YAML files from:", seo_dir)

        for yaml_file in seo_dir.glob("*.yaml"):
            print("Found file:", yaml_file)
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                print(f"Loaded {yaml_file.stem}:", data.keys() if data else None)
                content[yaml_file.stem] = data
        return content

    def get_page_seo(self, page_name):
        """Get SEO content for a specific page"""
        print(f"Getting page SEO for: {page_name}")
        return self._content.get("pages", {}).get(page_name, {})

    def get_location(self, location_name):
        """Get location-specific content"""
        return self._content.get("locations", {}).get(location_name.lower(), {})

    def get_base_info(self):
        """Get base business information"""
        return self._content.get("base_schema", {})

    def get_category_seo(self, category_slug):
        """Get SEO content for specific category"""
        return self._content.get("categories", {}).get(category_slug, {})

    def get_service_seo(self, service_name, package_name=None):
        """Get SEO content for services with fallbacks"""
        print("\nGetting SEO for service:", service_name)
        services = self._content.get("services", {})
        print("Available services:", services.keys())
        service_seo = services.get(service_name, {})
        print("Service SEO data:", service_seo)
        all_service_info = services.get("all_services", {})

        # Combine service-specific and general content
        seo_data = {
            "meta": {
                "title": f"Professional Photography | Stephen Lawson Photography",
                "description": "Professional photography services in Richmond, Virginia.",
            },
            "content": {
                "heading": "Professional Photography Services",
                "intro": "Quality photography services for all occasions",
            },
            **all_service_info,
        }

        # Update with service-specific content if available
        if service_seo:
            if "meta" in service_seo:
                seo_data["meta"].update(service_seo["meta"])
            if "content" in service_seo:
                seo_data["content"].update(service_seo["content"])

        # Add package-specific content if requested
        if package_name and "packages" in service_seo:
            package_seo = service_seo["packages"].get(package_name, {})
            if package_seo:
                seo_data["meta"].update(package_seo.get("meta", {}))
                seo_data["content"].update(package_seo.get("content", {}))

        return seo_data

    def get_schema(self, page_name):
        """Generate schema.org data for a page"""
        base = self.get_base_info()
        page = self.get_page_seo(page_name)

        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": base.get("business", {}).get("name"),
            "address": {
                "@type": "PostalAddress",
                **base.get("business", {}).get("address", {}),
            },
            "geo": {
                "@type": "GeoCoordinates",
                **base.get("business", {}).get("coordinates", {}),
            },
            **page.get("schema", {}),
        }

        return schema

    def get_full_seo(self, page_type, identifier, request=None):
        """Get complete SEO data for any page type"""
        base_info = self.get_base_info()
        location = self.get_location("richmond")

        if page_type == "service":
            seo_data = self.get_service_seo(identifier)
        elif page_type == "category":
            seo_data = self.get_category_seo(identifier)
        else:
            seo_data = self.get_page_seo(identifier)

        print(f"\nLoading SEO data for {page_type}: {identifier}")
        print(f"SEO Data found: {seo_data}")

        # Build complete SEO context
        full_seo = {
            "meta": {
                "title": seo_data.get("meta", {}).get("title"),
                "description": seo_data.get("meta", {}).get("description"),
                "keywords": seo_data.get("meta", {}).get(
                    "keywords"
                ),  # Explicitly include keywords
                "og_title": seo_data.get("meta", {}).get(
                    "og_title", seo_data.get("meta", {}).get("title")
                ),
                "og_description": seo_data.get("meta", {}).get(
                    "og_description", seo_data.get("meta", {}).get("description")
                ),
            },
            "content": seo_data.get("content", {}),
            "location": location,
            "business": base_info.get("business", {}),
            "structured_data": self.get_schema(identifier),
        }

        # Debug print the final SEO data
        print("\nFinal SEO data being returned:")
        print(f"Title: {full_seo['meta']['title']}")
        print(f"Keywords: {full_seo['meta']['keywords']}")
        print(f"Description: {full_seo['meta']['description']}")

        return full_seo

    def debug_seo_content(self):
        """Debug method to print SEO content"""
        print("\nSEO Content Debug:")
        print("=================")
        if not hasattr(self, "_content"):
            print("No content loaded")
            return

        print(f"Content keys: {list(self._content.keys())}")
        for key, value in self._content.items():
            print(f"\n{key}:")
            print("--------")
            print(f"Type: {type(value)}")
            print(f"Content: {value}")

    def get_service_seo(self, service_name, package_name=None):
        """Get SEO content for services with debugging"""
        print("\nGetting SEO for service:", service_name)
        services = self._content.get("services", {})
        print("Available services:", services.keys())
        service_seo = services.get(service_name, {})
        print("Service SEO data:", service_seo)

        # Default SEO data
        seo_data = {
            "meta": {
                "title": f"Professional Photography | Stephen Lawson Photography",
                "description": "Professional photography services in Richmond, Virginia.",
                "keywords": "richmond photographer, professional photography, virginia photographer",
            },
            "content": {
                "heading": "Professional Photography Services",
                "intro": "Quality photography services for all occasions",
            },
        }

        # Update with service-specific content if available
        if service_seo:
            if "meta" in service_seo:
                seo_data["meta"].update(service_seo["meta"])
            if "content" in service_seo:
                seo_data["content"].update(service_seo["content"])

        print("Final service SEO data:", seo_data)
        return seo_data
