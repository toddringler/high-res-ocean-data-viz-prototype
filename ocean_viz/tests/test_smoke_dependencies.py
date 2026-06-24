from ocean_viz import diagnostics


def test_dependency_check_has_expected_fields(monkeypatch):
    monkeypatch.setattr(diagnostics, "_check_imports", lambda: {"xarray": True})
    monkeypatch.setattr(diagnostics, "_check_cartopy_map", lambda: True)
    monkeypatch.setattr(diagnostics, "_check_xarray_open", lambda: True)
    monkeypatch.setattr(diagnostics, "_check_ffmpeg", lambda: True)
    monkeypatch.setattr(diagnostics, "_check_mp4_write", lambda: True)

    report = diagnostics.check_dependencies()
    assert report["python"] is True
    assert report["ok"] is True
