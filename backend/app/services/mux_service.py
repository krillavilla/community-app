import mux_python
from app.core.config import settings
class MuxService:
    """Handle video encoding with Mux"""

    def __init__(self):
        configuration = mux_python.Configuration()
        configuration.username = settings.MUX_TOKEN_ID
        configuration.password = settings.MUX_TOKEN_SECRET

        self.assets_api = mux_python.AssetsApi(
            mux_python.ApiClient(configuration)
        )

    def create_asset(self, video_url: str) -> dict:
        """Create Mux asset from video URL"""
        create_asset_request = mux_python.CreateAssetRequest(
            input=[mux_python.InputSettings(url=video_url)],
            playback_policy=[mux_python.PlaybackPolicy.PUBLIC]
        )

        asset = self.assets_api.create_asset(create_asset_request)

        return {
            'asset_id': asset.data.id,
            'playback_id': asset.data.playback_ids[0].id if asset.data.playback_ids else None,
            'status': asset.data.status
            }

    def get_asset_status(self, asset_id: str) -> str:
        """Check encoding status"""
        asset = self.assets_api.get_asset(asset_id)
        return asset.data.status #'preparing', 'ready', 'errored'


