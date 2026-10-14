using System.Globalization;

namespace PhotoGallery;

/// <summary>true → false і навпаки (для показу підказки, коли у фото немає GPS).</summary>
public class InvertBoolConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture) => value is not true;
    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture) => value is not true;
}
