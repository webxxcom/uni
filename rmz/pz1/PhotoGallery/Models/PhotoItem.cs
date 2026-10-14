namespace PhotoGallery.Models;

/// <summary>Фотографія в галереї разом із метаданими, прочитаними з EXIF.</summary>
public class PhotoItem
{
    public required string FilePath { get; init; }
    public string FileName => Path.GetFileName(FilePath);

    /// <summary>Дата зйомки з EXIF (DateTimeOriginal), або дата зміни файлу, якщо EXIF немає.</summary>
    public DateTime Date { get; init; }
    public bool DateFromExif { get; init; }

    public string? Camera { get; init; }
    public int? Width { get; init; }
    public int? Height { get; init; }
    public long SizeBytes { get; init; }

    /// <summary>GPS-координати місця зйомки (EXIF GPS IFD). null — у фото немає геолокації.</summary>
    public double? Latitude { get; init; }
    public double? Longitude { get; init; }
    public double? Altitude { get; init; }

    public bool HasLocation => Latitude is not null && Longitude is not null;

    public string Resolution => Width is > 0 && Height is > 0 ? $"{Width} × {Height}" : "—";
    public string SizeText => SizeBytes >= 1024 * 1024 ? $"{SizeBytes / 1024d / 1024:F1} МБ" : $"{SizeBytes / 1024d:F0} КБ";
    public string DateText => Date.ToString("dd.MM.yyyy HH:mm") + (DateFromExif ? "" : " (дата файлу)");
    public string CoordinatesText => HasLocation
        ? $"{Latitude:F6}, {Longitude:F6}"
        : "немає GPS-даних";

    /// <summary>Короткий підпис для рядка списку.</summary>
    public string Summary => $"{DateText} · {Camera ?? "камера невідома"}";
}
