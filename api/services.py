import httpx
import concurrent.futures
from typing import Dict, Any
from .exceptions import ExternalAPIException, InvalidProfileDataException

API_DISPLAY_NAMES = {
    "genderize": "Genderize",
    "agify": "Agify",
    "nationalize": "Nationalize",
}


class ProfileAggregatorService:
    @staticmethod
    def _get_age_group(age: int) -> str:
        if age <= 12: return "child"
        if age <= 19: return "teenager"
        if age <= 59: return "adult"
        return "senior"

    @classmethod
    def fetch_and_process_data(cls, name: str) -> Dict[str, Any]:
        urls = {
            "genderize": f"https://api.genderize.io?name={name}",
            "agify": f"https://api.agify.io?name={name}",
            "nationalize": f"https://api.nationalize.io?name={name}"
        }

        responses = {}
        with httpx.Client(timeout=10.0) as client:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_key = {executor.submit(client.get, url): key for key, url in urls.items()}
                for future in concurrent.futures.as_completed(future_to_key):
                    key = future_to_key[future]
                    display_name = API_DISPLAY_NAMES[key]
                    try:
                        response = future.result()
                        response.raise_for_status()
                        responses[key] = response.json()
                    except Exception:
                        raise ExternalAPIException(f"{display_name} returned an invalid response")

        g_data = responses.get("genderize", {})
        a_data = responses.get("agify", {})
        n_data = responses.get("nationalize", {})

        if not g_data.get("gender") or g_data.get("count", 0) == 0:
            raise InvalidProfileDataException("Genderize returned an invalid response")

        if a_data.get("age") is None:
            raise InvalidProfileDataException("Agify returned an invalid response")

        if not n_data.get("country"):
            raise InvalidProfileDataException("Nationalize returned an invalid response")

        top_country = max(n_data["country"], key=lambda c: c["probability"])

        return {
            "name": name,
            "gender": g_data["gender"],
            "gender_probability": g_data["probability"],
            "sample_size": g_data["count"],
            "age": a_data["age"],
            "age_group": cls._get_age_group(a_data["age"]),
            "country_id": top_country["country_id"],
            "country_probability": top_country["probability"],
        }