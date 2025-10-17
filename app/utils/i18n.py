from core.services.setting_services import SettingsService

_TRANSLATIONS = {
    'en': {
        'show': 'Show',
        'exit': 'Exit',
        'capture_saved': 'Capture {id} saved successfully!',
        'error': 'Error',
        'settings': 'Settings',
        'delete_selected': 'Delete selected',
        'no_capture_selected': 'No capture selected.',
        'confirm_removal_title': 'Confirm Removal',
        'confirm_removal_body': "Are you sure you want to remove '{title}'?\nAssociated captures will remain but lose their media.",
        'success': 'Success',
        'media_removed': 'Media removed successfully.',
        'apps_manager': 'Apps Manager',
        'existing_apps': 'Existing apps',
        'add_new_app': 'Add new app:',
        'new_app_placeholder': 'New app name...',
        'select_app': '✓ Select App',
        'remove_app': '✗ Remove App',
        'add': '+ Add',
        'attention': 'Attention',
        'empty_media_name': 'Media name cannot be empty.'
    },
    'pt': {
        # minimal Portuguese fallback (optional)
    }
}

# Add a few common UI button labels
_TRANSLATIONS['en'].update({
    'save': 'Save',
    'saving': 'Saving...',
    'saved': 'Saved'
})


def t(key: str, **kwargs) -> str:
    lang = SettingsService().user_settings.get('lang', 'en')
    text = _TRANSLATIONS.get(lang, {}).get(key, _TRANSLATIONS['en'].get(key, key))
    try:
        return text.format(**kwargs)
    except Exception:
        return text
