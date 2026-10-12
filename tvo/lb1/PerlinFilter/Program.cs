using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.Globalization;
using System.Runtime.InteropServices;
using PerlinFilter;

// ЛР №1 ТВО, варіант 9: накладання шуму Перліна на зображення в кількох потоках.
// Запуск: dotnet run -c Release -- <вхідне зображення> <тека результатів> [кількість повторів]

string input = args.Length > 0 ? args[0] : "input.jpg";
string outDir = args.Length > 1 ? args[1] : "results";
int repeats = args.Length > 2 ? int.Parse(args[2]) : 7;
int[] threadCounts = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16];
Directory.CreateDirectory(outDir);

// Параметри фільтра.
const double Scale = 1.0 / 160; // розмір найбільшої «плями» шуму ≈ 160 пікселів
const int Octaves = 6;
const double Persistence = 0.5;
const double Strength = 70; // наскільки сильно шум змінює яскравість (0..255)
var perlin = new Perlin(seed: 9);

// Читаємо зображення в масив байтів BGR (24 біти на піксель).
using var bmp = new Bitmap(input);
int width = bmp.Width, height = bmp.Height;
var rect = new Rectangle(0, 0, width, height);
var data = bmp.LockBits(rect, ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
int stride = data.Stride;
byte[] src = new byte[stride * height];
Marshal.Copy(data.Scan0, src, 0, src.Length);
bmp.UnlockBits(data);

Console.WriteLine($"Зображення {width}x{height}, логічних процесорів: {Environment.ProcessorCount}");

// Обробка рядків [y0; y1). Кожен потік пише лише у свої рядки dst, тому синхронізація не потрібна.
void ProcessRows(byte[] dst, int y0, int y1)
{
    for (int y = y0; y < y1; y++)
    {
        int row = y * stride;
        for (int x = 0; x < width; x++)
        {
            double n = perlin.Fractal(x * Scale, y * Scale, Octaves, Persistence);
            int delta = (int)Math.Round(Strength * n);
            int i = row + x * 3;
            dst[i] = Clamp(src[i] + delta);
            dst[i + 1] = Clamp(src[i + 1] + delta);
            dst[i + 2] = Clamp(src[i + 2] + delta);
        }
    }
}

static byte Clamp(int v) => (byte)(v < 0 ? 0 : v > 255 ? 255 : v);

// Зображення ділиться на p горизонтальних смуг однакової висоти, по одній на потік.
double RunWithThreads(byte[] dst, int p)
{
    var sw = Stopwatch.StartNew();
    var threads = new Thread[p];
    for (int t = 0; t < p; t++)
    {
        int y0 = height * t / p, y1 = height * (t + 1) / p;
        threads[t] = new Thread(() => ProcessRows(dst, y0, y1));
        threads[t].Start();
    }
    foreach (var th in threads) th.Join();
    sw.Stop();
    return sw.Elapsed.TotalMilliseconds;
}

// Еталон: один потік. Перший прогін також «прогріває» JIT.
byte[] reference = new byte[src.Length];
RunWithThreads(reference, 1);

var lines = new List<string> { "threads;median_ms;min_ms;max_ms;speedup;efficiency;equal_to_1_thread" };
double t1 = 0;
foreach (int p in threadCounts)
{
    var times = new double[repeats];
    byte[] dst = new byte[src.Length];
    for (int r = 0; r < repeats; r++) times[r] = RunWithThreads(dst, p);
    Array.Sort(times);
    double median = times[repeats / 2];
    if (p == 1) t1 = median;
    bool same = dst.AsSpan().SequenceEqual(reference);
    double s = t1 / median, e = s / p;
    Console.WriteLine($"p={p,2}: медіана {median,8:F1} мс, S={s:F2}, E={e:F2}, збіг з 1 потоком: {same}");
    lines.Add(string.Join(';', p, F(median), F(times[0]), F(times[^1]), F(s), F(e), same));
}
File.WriteAllLines(Path.Combine(outDir, "results.csv"), lines);

static string F(double v) => v.ToString("F3", CultureInfo.InvariantCulture);

// Зберігаємо результат фільтра і окремо сам шум (для звіту).
SaveBgr(reference, Path.Combine(outDir, "output.jpg"));
byte[] noiseOnly = new byte[src.Length];
for (int y = 0; y < height; y++)
    for (int x = 0; x < width; x++)
    {
        byte g = Clamp((int)Math.Round(127.5 + 127.5 * perlin.Fractal(x * Scale, y * Scale, Octaves, Persistence)));
        int i = y * stride + x * 3;
        noiseOnly[i] = noiseOnly[i + 1] = noiseOnly[i + 2] = g;
    }
SaveBgr(noiseOnly, Path.Combine(outDir, "noise.jpg"));
Console.WriteLine($"Результати збережено в {Path.GetFullPath(outDir)}");

void SaveBgr(byte[] pixels, string path)
{
    using var img = new Bitmap(width, height, PixelFormat.Format24bppRgb);
    var d = img.LockBits(rect, ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
    Marshal.Copy(pixels, 0, d.Scan0, pixels.Length);
    img.UnlockBits(d);
    img.Save(path, ImageFormat.Jpeg);
}
