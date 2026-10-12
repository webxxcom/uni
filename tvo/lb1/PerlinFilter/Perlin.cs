namespace PerlinFilter;

/// <summary>
/// Шум Перліна (покращена версія К. Перліна, 2002) та фрактальна сума октав.
/// Клас незмінний після створення, тому його можна безпечно читати з багатьох потоків.
/// </summary>
public sealed class Perlin
{
    private readonly int[] _p = new int[512]; // таблиця перестановок, продубльована, щоб не робити & 255 двічі

    public Perlin(int seed)
    {
        var perm = new int[256];
        for (int i = 0; i < 256; i++) perm[i] = i;
        var rnd = new Random(seed);
        for (int i = 255; i > 0; i--) // перемішування Фішера–Єйтса
        {
            int j = rnd.Next(i + 1);
            (perm[i], perm[j]) = (perm[j], perm[i]);
        }
        for (int i = 0; i < 512; i++) _p[i] = perm[i & 255];
    }

    // Згладжувальна крива 6t^5 - 15t^4 + 10t^3: неперервні перша і друга похідні.
    private static double Fade(double t) => t * t * t * (t * (t * 6 - 15) + 10);

    private static double Lerp(double t, double a, double b) => a + t * (b - a);

    // Скалярний добуток псевдовипадкового градієнта (одного з 4 діагональних) на вектор відстані (x, y).
    private static double Grad(int hash, double x, double y) => (hash & 3) switch
    {
        0 => x + y,
        1 => -x + y,
        2 => x - y,
        _ => -x - y,
    };

    /// <summary>Двовимірний шум Перліна, значення приблизно в [-1; 1].</summary>
    public double Noise(double x, double y)
    {
        int xi = (int)Math.Floor(x), yi = (int)Math.Floor(y);
        double xf = x - xi, yf = y - yi;
        xi &= 255; yi &= 255;

        double u = Fade(xf), v = Fade(yf);

        // Хеші чотирьох кутів клітинки решітки.
        int aa = _p[_p[xi] + yi], ab = _p[_p[xi] + yi + 1];
        int ba = _p[_p[xi + 1] + yi], bb = _p[_p[xi + 1] + yi + 1];

        double x1 = Lerp(u, Grad(aa, xf, yf), Grad(ba, xf - 1, yf));
        double x2 = Lerp(u, Grad(ab, xf, yf - 1), Grad(bb, xf - 1, yf - 1));
        return Lerp(v, x1, x2);
    }

    /// <summary>
    /// Фрактальний шум (fBm): сума октав, у кожній частота ×2, амплітуда ×persistence.
    /// Результат нормовано до [-1; 1].
    /// </summary>
    public double Fractal(double x, double y, int octaves, double persistence)
    {
        double sum = 0, amp = 1, freq = 1, norm = 0;
        for (int o = 0; o < octaves; o++)
        {
            sum += amp * Noise(x * freq, y * freq);
            norm += amp;
            amp *= persistence;
            freq *= 2;
        }
        return sum / norm;
    }
}
