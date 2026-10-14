using System.Collections.ObjectModel;
using System.Text.Json;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PhotoGallery.Models;
using PhotoGallery.Services;

namespace PhotoGallery.ViewModels;

/// <summary>Галерея: список фотографій, додавання/видалення, перехід до перегляду.</summary>
public partial class MainViewModel : ObservableObject
{
    private const string PrefsKey = "photo_paths";
    private readonly ExifService _exif;

    public ObservableCollection<PhotoItem> Photos { get; } = [];

    public IEnumerable<PhotoItem> WithLocation => Photos.Where(p => p.HasLocation).OrderByDescending(p => p.Date);
    public IEnumerable<PhotoItem> WithoutLocation => Photos.Where(p => !p.HasLocation).OrderByDescending(p => p.Date);

    [ObservableProperty]
    public partial bool IsBusy { get; set; }

    public MainViewModel(ExifService exif)
    {
        _exif = exif;
        Photos.CollectionChanged += (_, _) =>
        {
            OnPropertyChanged(nameof(WithLocation));
            OnPropertyChanged(nameof(WithoutLocation));
            Save();
        };
    }

    /// <summary>Відновлює список з попереднього запуску (шляхи зберігаються в Preferences).</summary>
    public async Task LoadAsync()
    {
        var paths = JsonSerializer.Deserialize<List<string>>(Preferences.Default.Get(PrefsKey, "[]")) ?? [];
        // Для демонстрації та скриншотів: змінна середовища з текою прикладів.
        var demo = Environment.GetEnvironmentVariable("PHOTO_GALLERY_FOLDER");
        if (!string.IsNullOrEmpty(demo) && System.IO.Directory.Exists(demo))
            paths.AddRange(System.IO.Directory.EnumerateFiles(demo).Where(IsImage));
        await AddAsync(paths.Where(File.Exists).Distinct(StringComparer.OrdinalIgnoreCase));
    }

    [RelayCommand]
    private async Task AddPhotos()
    {
        var files = await FilePicker.Default.PickMultipleAsync(new PickOptions
        {
            PickerTitle = "Оберіть фотографії",
            FileTypes = FilePickerFileType.Images,
        });
        if (files is null) return;
        await AddAsync(files.Where(f => f is not null).Select(f => f!.FullPath));
    }

    [RelayCommand]
    private void Remove(PhotoItem photo) => Photos.Remove(photo);

    [RelayCommand]
    private void Clear() => Photos.Clear();

    [RelayCommand]
    private Task Open(PhotoItem photo) =>
        Shell.Current.GoToAsync(nameof(Views.PhotoPage), new Dictionary<string, object> { ["Photo"] = photo });

    private async Task AddAsync(IEnumerable<string> paths)
    {
        IsBusy = true;
        try
        {
            var known = Photos.Select(p => p.FilePath).ToHashSet(StringComparer.OrdinalIgnoreCase);
            var fresh = paths.Where(p => known.Add(p)).ToList();
            // Читання EXIF — робота з файлами, тому у фоновому потоці, щоб не блокувати інтерфейс.
            var items = await Task.Run(() => fresh.Select(_exif.Read).ToList());
            foreach (var item in items) Photos.Add(item);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private void Save() =>
        Preferences.Default.Set(PrefsKey, JsonSerializer.Serialize(Photos.Select(p => p.FilePath)));

    private static bool IsImage(string path) =>
        Path.GetExtension(path).ToLowerInvariant() is ".jpg" or ".jpeg" or ".png" or ".heic" or ".webp" or ".tif" or ".tiff";
}
