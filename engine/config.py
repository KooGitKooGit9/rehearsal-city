"""데모 지역 설정. 지역을 바꾸려면 이 파일의 DEMO_REGION만 수정한다 (하드코딩 금지 원칙)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"


@dataclass(frozen=True)
class RegionConfig:
    slug: str
    # Nominatim 지오코딩 쿼리. 한글 행정동명("성수동, 성동구, 서울특별시")은 0 결과를 반환하므로
    # OSM이 인식하는 영문 표기를 사용해야 한다.
    place_query: str
    network_type: str = "walk"

    @property
    def cache_path(self) -> Path:
        return CACHE_DIR / f"{self.slug}_{self.network_type}.graphml"

    @property
    def citizens_path(self) -> Path:
        return CACHE_DIR / f"{self.slug}_citizens.geojson"

    @property
    def pois_path(self) -> Path:
        return CACHE_DIR / f"{self.slug}_pois.geojson"


DEMO_REGION = RegionConfig(
    slug="seongsu",
    place_query="Seongsu-dong, Seongdong-gu, Seoul, South Korea",
)
