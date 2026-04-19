"""
Configuration for Perplexity AI integration.
"""

# Optional: Add your Perplexity account cookies here
PERPLEXITY_COOKIES = {
    'pplx.visitor-id': '6517cd0c-1d36-4eac-8f40-7f18fb78a0e9',
    'sidebarHiddenHubs': '[]',
    '__stripe_mid': '3953fa2c-3b47-46a7-a5d1-f5710ccfa0ccd63b0d',
    'g_state': '{"i_l":0,"i_ll":1767830237757,"i_b":"WgkBu34HUpqa0ONeYAMU6KsGQtK/mpASyeIpB/Qpbl0","i_e":{"enable_itp_optimization":0}}',
    'gov-badge': '3',
    'pplx.personal-search-badge-seen': '{%22sidebar%22:true%2C%22settingsSidebar%22:false%2C%22personalize%22:false}',
    'pplx.tasks-settings-seen': 'true',
    'intercom-id-l2wyozh0': '80c988c9-9981-4870-ad8d-eae475342361',
    'intercom-device-id-l2wyozh0': '27315cd3-a111-49e1-a70d-5eb9ba1b29a3',
    'finance-alert-page-visit': '1',
    'unify_session_id': '1a47909b-1b46-49e8-b9ab-e53a5f67da8a',
    'IndrX2c1OFdjNG9oXzgxd1JocUVVWGFadkNMVEZaYlkzeGRCUlRlR1JldWhCX3VuaWZ5X3Nlc3Npb25faWQi': 'IjFhNDc5MDliLTFiNDYtNDllOC1iOWFiLWU1M2E1ZjY3ZGE4YSI=',
    'unify_visitor_id': 'e84a6a1b-076d-4474-b348-65c388d5351f',
    'IndrX2c1OFdjNG9oXzgxd1JocUVVWGFadkNMVEZaYlkzeGRCUlRlR1JldWhCX3VuaWZ5X3Zpc2l0b3JfaWQi': 'ImU4NGE2YTFiLTA3NmQtNDQ3NC1iMzQ4LTY1YzM4OGQ1MzUxZiI=',
    'pplx.edge-vid': '78a40ab2-46da-4154-9b1a-6e178bd9b2b7',
    'computer-button-popover-shown': '1',
    'pplx.trackingAllowed': 'true',
    '__cflb': '02DiuDyvFMmK5p9jVbVnMNSKYZhUL9aGka2hx692C5uFS',
    'pplx.session-id': 'a68b2804-c211-4823-99d1-8db083c98b50',
    '__cf_bm': '3d7cWpv0CCotsbebbSiSitruAB0_PzXz3Hr0cREOcAY-1776500956-1.0.1.1-Gpbj32mkO1vsXdO0PN24f3sdIhuKkYktqoVA18Qq3ZL8Lw3Fj0VCveV_8LEviRGEvd1wLDT.fID3PGfSNw7jSy7RirWQ_EjtMPFMl_OPL2A',
    'pplx.edge-sid': '06cb45ab-324e-48d7-bc84-45b3bca54524',
    'homepage-computer-primers-impressions': '13',
    'cf_clearance': 'GeNWtkN_XJoPoGjwn1bEv0xEAdhpnAac_dEeOFsZODk-1776501002-1.2.1.1-BiLzRdCgNoakghaU7zLUoKcN9362EnoMn58tfOAS2lTCIiGHRtRGy537WRO3R2xyqyt0hlYLlT0wNO90EztFo8FcYg6OBw22woyvYqNJGp3yVVDj2CY7DxC1GrnoHZCjVHuCH4yOkZJ0LeSUpNdc2Dvfl1SM5VGOx0oFHLZmLq37pS1szSPo1BNUPuMH2xQGi8RTtcLFv0sGMNI9E5h0bB.h5PfEyxMw65pmAmmYltbjIl1HIvgZoiP8V67TTZ24.jOG5D6NlNdU2NsDf6I.YI4KN_VTxS0BQovExQ1DaaUK7.lgVUfPkNuEIR.ar8o1Fs8Bj6LgdtiTImDu.duDqQ',
    'pplx.metadata': '{%22qc%22:740%2C%22qcu%22:1511%2C%22qcm%22:146%2C%22qcc%22:1463%2C%22qcco%22:0%2C%22qccol%22:0%2C%22qcdr%22:34%2C%22qcs%22:0%2C%22qcg%22:0%2C%22qcd%22:2%2C%22hli%22:true%2C%22hcga%22:false%2C%22hcds%22:false%2C%22hso%22:false%2C%22hfo%22:false%2C%22hsco%22:false%2C%22hfco%22:false%2C%22hsma%22:false%2C%22hdc%22:true%2C%22hdttb%22:false%2C%22hsttb%22:false%2C%22fqa%22:1759455074660%2C%22lqa%22:1776501070149}',
    '__Secure-next-auth.session-token': 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..5E1BkHM8bdSwDHWM.-R56AZanE497_dGvayzyLzedVnrnr_OLKbviiGXjlQqg5p1yWMxXRTGXBu7HRd0UHDXCNGc3axRUkWiq7oIK6BqlDLnDDp5tuKoJ3FRCuGs1MMO6jISxVeIdhqtB-9CPz4CnuQqNNJz46q8foFbhB6l-6TaPMBHkxTc0XRN2sgjmX2N9teZ6-dmsJdpMRVBVpY4Q54MuSwyyFBh5RT2xJ4N54YAUbwNvkUKUy-AkwARE117kgcsXMbEIT-4KedXQ4ydMZ6Lp4-vtgRyaiuC3o9eNLf5MfTIlFzmt6Qsaqwpz7_7DM4k70HNlbb0PsvQ8.KamM2aovInTT50Mt_1gzjw',
    '_dd_s': '',
}

# Default search mode: 'auto', 'pro', 'reasoning', 'deep research'
DEFAULT_MODE = "auto"

# Default sources: 'web', 'scholar', 'social'
DEFAULT_SOURCES = ["web"]

# Batch processing configuration
BATCH_SIZE = 50
BATCH_DELAY_SECONDS = 5
BATCH_MODE = "pro"
BATCH_MODEL = None

# Processing range bounds (optional - set to None to process all items)
# PROCESS_START_INDEX: First item index to process (1-based, inclusive)
# PROCESS_END_INDEX: Last item index to process (1-based, inclusive)
# Example: PROCESS_START_INDEX = 1001, PROCESS_END_INDEX = 2000 processes items 1001-2000 only
PROCESS_START_INDEX = 1  # None = start from beginning
PROCESS_END_INDEX = 50_000    # None = process until end

# File paths
WORDS_INPUT_FILE = "raw/words.txt"
WORDS_OUTPUT_DIR = "output/words"
PROMPT_TEMPLATE_FILE = "words-extraction-prompt.md"
BATCH_STATE_FILE = "batch_config.json"

# Default language
DEFAULT_LANGUAGE = "en-US"
