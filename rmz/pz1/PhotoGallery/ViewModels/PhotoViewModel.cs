using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PhotoGallery.Models;
using PhotoGallery.Services;

namespace PhotoGallery.ViewModels;

/// <summary>Перегляд однієї фотографії: зображення, EXIF і місце зйомки на карті.</summary>
[QueryProperty(nameof(Photo), "Photo")]
public partial class PhotoViewModel : ObservableObject
{
    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(MapSource))]
    public partial PhotoItem? Photo { get; set; }

    /// <summary>
    /// Карта для WebView: Leaflet + тайли Esri World Street Map (без ключа API) з міткою в місці зйомки.
    /// Елемент Map із Microsoft.Maui.Controls.Maps на Windows не підтримується, тому для всіх платформ — WebView.
    /// (tile.openstreetmap.org і вбудована карта OSM блокують запити з WebView; CARTO вимагає ключ.)
    /// </summary>
    public HtmlWebViewSource? MapSource => Photo is { HasLocation: true } p
        ? new HtmlWebViewSource { Html = BuildMapHtml(p.Latitude!.Value, p.Longitude!.Value, p.FileName) }
        : null;

    [RelayCommand]
    private async Task OpenInMaps()
    {
        if (Photo is not { HasLocation: true } p) return;
        // Відкриває системний застосунок карт (Windows Maps, Google Maps, Apple Maps) у точці зйомки.
        var opened = await Map.Default.TryOpenAsync(new Location(p.Latitude!.Value, p.Longitude!.Value),
            new MapLaunchOptions { Name = p.FileName });
        if (!opened)
            await Shell.Current.DisplayAlertAsync("Карти", "Не вдалося відкрити застосунок карт на цьому пристрої.", "OK");
    }

    [RelayCommand]
    private Task CopyCoordinates() => Photo is { HasLocation: true } p
        ? Clipboard.Default.SetTextAsync($"{ExifService.Invariant(p.Latitude!.Value)}, {ExifService.Invariant(p.Longitude!.Value)}")
        : Task.CompletedTask;

    public static string BuildMapHtml(double lat, double lon, string title)
    {
        string la = ExifService.Invariant(lat), lo = ExifService.Invariant(lon);
        var safeTitle = System.Net.WebUtility.HtmlEncode(title);
        return $$"""
            <!doctype html>
            <html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>html,body,#map{height:100%;margin:0}</style></head>
            <body><div id="map"></div><script>
              var map = L.map('map').setView([{{la}}, {{lo}}], 16);
              L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
                { maxZoom: 19, attribution: 'Tiles &copy; Esri' }).addTo(map);
              L.marker([{{la}}, {{lo}}]).addTo(map).bindPopup('{{safeTitle}}<br>{{la}}, {{lo}}').openPopup();
              L.circle([{{la}}, {{lo}}], { radius: 100, color: '#1f4e9c', fillOpacity: 0.12 }).addTo(map);
            </script></body></html>
            """;
    }
}
