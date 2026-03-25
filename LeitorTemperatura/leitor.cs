using System;
using System.IO;
using System.Linq;
using System.Threading;

class LeitorTemperatura
{
    static void Main(string[] args)
    {
        string caminhoBase = "/sys/bus/w1/devices/";

        string pastaSensor = BuscarPastaDoSensor(caminhoBase);

        if (pastaSensor == null)
        {
            Console.WriteLine("❌ Sensor de temperatura não encontrado.");
            return;
        }

        string arquivoLeitura = Path.Combine(pastaSensor, "w1_slave");

        Console.WriteLine("✅ Sensor encontrado! Iniciando leitura...\n");

        while (true)
        {
            double? temperatura = LerTemperatura(arquivoLeitura);

            if (temperatura.HasValue)
            {
                Console.WriteLine($"🌡️ Temperatura: {temperatura.Value:F2} °C");
            }
            else
            {
                Console.WriteLine("⚠️ Erro ao ler temperatura.");
            }

            Thread.Sleep(2000); // espera 2 segundos
        }
    }

    // 🔍 Busca a pasta do sensor (DS18B20 começa com "28-")
    static string BuscarPastaDoSensor(string caminhoBase)
    {
        return Directory.GetDirectories(caminhoBase)
                        .FirstOrDefault(pasta => pasta.Contains("28-"));
    }

    // 📖 Faz a leitura da temperatura
    static double? LerTemperatura(string caminhoArquivo)
    {
        try
        {
            string[] linhas = File.ReadAllLines(caminhoArquivo);

            // Verifica se a leitura é válida
            bool leituraValida = linhas[0].EndsWith("YES");

            if (!leituraValida)
                return null;

            // Procura o valor da temperatura (t=xxxxx)
            int indiceTemperatura = linhas[1].IndexOf("t=");

            if (indiceTemperatura == -1)
                return null;

            string valorBruto = linhas[1].Substring(indiceTemperatura + 2);

            double temperaturaCelsius = double.Parse(valorBruto) / 1000.0;

            return temperaturaCelsius;
        }
        catch
        {
            return null;
        }
    }
}