using System.Globalization;
using MetadataExtractor;
using MetadataExtractor.Formats.Exif;
using MetadataExtractor.Formats.Jpeg;
using PhotoGallery.Models;
using Directory = MetadataExtractor.Directory;

namespace PhotoGallery.Services;

/// <summary>
/// Читає метадані зображення бібліотекою MetadataExtractor (https://github.com/drewnoakes/metadata-extractor-dotnet):
/// камеру, дату зйомки, розмір і GPS-координати (EXIF GPS IFD).
/// </summary>
public class ExifService
{
    public PhotoItem Read(string path)
    {
        var info = new FileInfo(path);
        IReadOnlyList<Directory> dirs;
        try
        {
            dirs = ImageMetadataReader.ReadMetadata(path);
        }
        catch (ImageProcessingException)
        {
            dirs = []; // не зображення або пошкоджений файл — показуємо без метаданих
        }

        var ifd0 = dirs.OfType<ExifIfd0Directory>().FirstOrDefault();
        var subIfd = dirs.OfType<ExifSubIfdDirectory>().FirstOrDefault();
        var gps = dirs.OfType<GpsDirectory>().FirstOrDefault();

        DateTime? taken = null;
        if (subIfd?.TryGetDateTime(ExifDirectoryBase.TagDateTimeOriginal, out var dt) == true) taken = dt;
        else if (ifd0?.TryGetDateTime(ExifDirectoryBase.TagDateTime, out var dt2) == true) taken = dt2;

        string? camera = null;
        var make = ifd0?.GetDescription(ExifDirectoryBase.TagMake)?.Trim();
        var model = ifd0?.GetDescription(ExifDirectoryBase.TagModel)?.Trim();
        if (!string.IsNullOrEmpty(model))
            camera = !string.IsNullOrEmpty(make) && !model.StartsWith(make, StringComparison.OrdinalIgnoreCase) ? $"{make} {model}" : model;

        int? width = null, height = null;
        var jpeg = dirs.OfType<JpegDirectory>().FirstOrDefault();
        if (jpeg is not null)
        {
            width = jpeg.GetImageWidth();
            height = jpeg.GetImageHeight();
        }
        else if (subIfd?.TryGetInt32(ExifDirectoryBase.TagExifImageWidth, out var w) == true &&
                 subIfd.TryGetInt32(ExifDirectoryBase.TagExifImageHeight, out var h))
        {
            width = w;
            height = h;
        }

        double? lat = null, lon = null, alt = null;
        // TryGetGeoLocation сам переводить градуси/хвилини/секунди в десяткові та враховує N/S, E/W.
        if (gps?.TryGetGeoLocation(out var geo) == true && !geo.IsZero)
        {
            lat = geo.Latitude;
            lon = geo.Longitude;
        }
        if (gps?.TryGetRational(GpsDirectory.TagAltitude, out var a) == true)
            alt = a.ToDouble() * (gps.TryGetInt32(GpsDirectory.TagAltitudeRef, out var aref) && aref == 1 ? -1 : 1);

        return new PhotoItem
        {
            FilePath = path,
            Date = taken ?? info.LastWriteTime,
            DateFromExif = taken is not null,
            Camera = camera,
            Width = width,
            Height = height,
            SizeBytes = info.Exists ? info.Length : 0,
            Latitude = lat,
            Longitude = lon,
            Altitude = alt,
        };
    }

    /// <summary>Координати для URL/JS — завжди з крапкою незалежно від мови системи.</summary>
    public static string Invariant(double v) => v.ToString("0.######", CultureInfo.InvariantCulture);
}
