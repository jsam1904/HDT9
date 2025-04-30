# -----------------------------------------------------------------------------
# Archivo: HDT-9.PY
# Descripción: Implementación de un compresor y descompresor basado en el 
#              algoritmo de Huffman. Incluye funciones para compresión, 
#              descompresión, serialización y deserialización del árbol de Huffman.
# Creadores: Javier Alvarado - 24546, Juan Montenegro - 24750
# -----------------------------------------------------------------------------

from bitarray import bitarray
import unittest

print("Compresor HUFFMAN")

# -----------------------------------------------------------------------------
# Función: frecuencia
# Descripción: Calcula la frecuencia de cada carácter en un texto dado.
# Parámetros:
#   - texto: Cadena de texto a analizar.
# Retorna:
#   - Diccionario con las frecuencias de cada carácter.
# -----------------------------------------------------------------------------
def frecuencia(texto):
    frecuencias = {}
    for caracter in texto:
        if caracter in frecuencias:
            frecuencias[caracter] += 1
        else:
            frecuencias[caracter] = 1
    return frecuencias

# -----------------------------------------------------------------------------
# Función: crear_nodo
# Descripción: Crea una lista de nodos a partir de las frecuencias de los caracteres.
# Parámetros:
#   - frecuencias: Diccionario con las frecuencias de los caracteres.
# Retorna:
#   - Lista de nodos (tuplas de frecuencia y carácter).
# -----------------------------------------------------------------------------
def crear_nodo(frecuencias):
    nodos = []
    for caracter, frecuencia in frecuencias.items():
        nodos.append((frecuencia, caracter))
    return nodos

# -----------------------------------------------------------------------------
# Función: crear_arbol
# Descripción: Construye el árbol de Huffman a partir de una lista de nodos.
# Parámetros:
#   - nodos: Lista de nodos (tuplas de frecuencia y carácter).
# Retorna:
#   - Nodo raíz del árbol de Huffman.
# -----------------------------------------------------------------------------
def crear_arbol(nodos):
    while len(nodos) > 1:
        nodos.sort(key=lambda x: x[0])  # Ordenar por frecuencia
        izquierda = nodos.pop(0)  # Nodo con menor frecuencia
        derecha = nodos.pop(0)  # Segundo nodo con menor frecuencia
        nuevo_nodo = (izquierda[0] + derecha[0], (izquierda, derecha))
        nodos.append(nuevo_nodo)
    return nodos[0]

# -----------------------------------------------------------------------------
# Función: generar_codigos
# Descripción: Genera los códigos de Huffman para cada carácter.
# Parámetros:
#   - nodo: Nodo raíz del árbol de Huffman.
#   - codigo_actual: Código actual (bitarray).
#   - codigos: Diccionario donde se almacenarán los códigos generados.
# -----------------------------------------------------------------------------
def generar_codigos(nodo, codigo_actual, codigos):
    if isinstance(nodo[1], str):  # Nodo hoja
        codigos[nodo[1]] = codigo_actual.to01() or '0'  # Evitar códigos vacíos
    else:
        generar_codigos(nodo[1][0], codigo_actual + bitarray('0'), codigos)  # Izquierda
        generar_codigos(nodo[1][1], codigo_actual + bitarray('1'), codigos)  # Derecha

# -----------------------------------------------------------------------------
# Función: serializar_arbol
# Descripción: Serializa el árbol de Huffman y lo guarda en un archivo.
# Parámetros:
#   - nodo: Nodo raíz del árbol de Huffman.
#   - archivo: Archivo donde se guardará el árbol serializado.
# -----------------------------------------------------------------------------
def serializar_arbol(nodo, archivo):
    if isinstance(nodo[1], str):  # Nodo hoja
        char = nodo[1]
        if char in [' ', '\n', '\t', '\\']:  # Escapar caracteres especiales
            archivo.write(f"L\\{ord(char)} ")
        else:
            archivo.write(f"L{char} ")
    else:  # Nodo interno
        archivo.write("I ")
        serializar_arbol(nodo[1][0], archivo)  # Izquierda
        serializar_arbol(nodo[1][1], archivo)  # Derecha

# -----------------------------------------------------------------------------
# Función: deserializar_arbol
# Descripción: Deserializa un árbol de Huffman desde un archivo.
# Parámetros:
#   - archivo: Archivo que contiene el árbol serializado.
# Retorna:
#   - Nodo raíz del árbol de Huffman y la longitud del texto original.
# -----------------------------------------------------------------------------
def deserializar_arbol(archivo):
    content = archivo.read().strip()
    if not content:  # Handle empty file
        return None, 0
    lines = content.split('\n')
    if len(lines) < 2:  # Ensure there's a tree and length
        tokens = lines[0].split() if lines else []
        text_length = 0
    else:
        tokens = lines[0].split()
        text_length = int(lines[1]) if lines[1].strip() else 0
    
    def construir_arbol(index):
        if index[0] >= len(tokens):
            return None, index
        token = tokens[index[0]]
        index[0] += 1
        if token.startswith('L'):  # Nodo hoja
            if token.startswith('L\\'):  # Carácter escapado
                char = chr(int(token[2:]))
            else:
                char = token[1]
            return (0, char), index
        else:  # Nodo interno
            izquierda, index = construir_arbol(index)
            derecha, index = construir_arbol(index)
            if izquierda is None or derecha is None:
                return None, index
            return (izquierda[0] + derecha[0], (izquierda, derecha)), index
    
    arbol, _ = construir_arbol([0])
    return arbol, text_length

# -----------------------------------------------------------------------------
# Función: comprimir
# Descripción: Comprime un texto utilizando el algoritmo de Huffman.
# Parámetros:
#   - texto: Texto a comprimir.
# Retorna:
#   - Objeto bitarray con el texto comprimido.
# -----------------------------------------------------------------------------
def comprimir(texto):
    if not texto:  # Handle empty input
        with open("arbol.hufftree", "w", encoding='utf-8') as f:
            f.write("\n0")
        return bitarray()
    
    frecuencias = frecuencia(texto)
    nodos = crear_nodo(frecuencias)
    arbol = crear_arbol(nodos)
    codigos = {}
    generar_codigos(arbol, bitarray(), codigos)
    
    # Guardar el árbol y la longitud del texto
    with open("arbol.hufftree", "w", encoding='utf-8') as f:
        serializar_arbol(arbol, f)
        f.write(f"\n{len(texto)}")  # Guardar longitud al final
    
    huffman = bitarray()
    for caracter in texto:
        huffman.extend(codigos[caracter])
    return huffman

# -----------------------------------------------------------------------------
# Función: descomprimir
# Descripción: Descomprime un archivo comprimido utilizando el árbol de Huffman.
# Parámetros:
#   - archivo_comprimido: Archivo binario comprimido.
#   - archivo_arbol: Archivo que contiene el árbol de Huffman serializado.
# Retorna:
#   - Texto descomprimido.
# -----------------------------------------------------------------------------
def descomprimir(archivo_comprimido, archivo_arbol):
    # Leer el árbol y la longitud del texto
    with open(archivo_arbol, "r", encoding='utf-8') as f:
        arbol, longitud_texto = deserializar_arbol(f)
    
    if arbol is None or longitud_texto == 0:  # Handle empty or invalid tree
        return ""
    
    # Leer el archivo comprimido
    with open(archivo_comprimido, "rb") as f:
        huffman = bitarray()
        huffman.fromfile(f)
    
    # Descomprimir usando el árbol
    texto = []
    nodo_actual = arbol
    for bit in huffman:
        if bit == 0:
            nodo_actual = nodo_actual[1][0]  # Ir a la izquierda
        else:
            nodo_actual = nodo_actual[1][1]  # Ir a la derecha
        
        if isinstance(nodo_actual[1], str):  # Nodo hoja
            texto.append(nodo_actual[1])
            nodo_actual = arbol  # Volver a la raíz
            if len(texto) == longitud_texto:  # Parar cuando se alcanza la longitud
                break
    
    return ''.join(texto)

# -----------------------------------------------------------------------------
# Función: leer_archivo
# Descripción: Lee el contenido de un archivo de texto.
# Parámetros:
#   - archivo: Ruta del archivo a leer.
# Retorna:
#   - Contenido del archivo como cadena de texto.
# -----------------------------------------------------------------------------
def leer_archivo(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        texto = f.read()
    return texto

# -----------------------------------------------------------------------------
# Función: main
# Descripción: Menú principal para interactuar con el compresor y descompresor.
# -----------------------------------------------------------------------------
def main():
    opcion = 0
    while opcion != 3:
        print("")
        print("Menú")
        print("1. Comprimir")
        print("2. Descomprimir")
        print("3. Salir")
        opcion = int(input("Seleccione una opción: "))
        print("")

        if opcion == 1:
            try:
                texto = leer_archivo("texto.txt")
                huffman = comprimir(texto)
                with open("booleanos.huff", "wb") as archivo:
                    huffman.tofile(archivo)
                print("Texto original:", texto)
                print("Archivo comprimido creado exitosamente: booleanos.huff")
                print("Archivo árbol creado exitosamente: arbol.hufftree")
            except Exception as e:
                print(f"Error al comprimir: {e}")

        elif opcion == 2:
            try:
                texto_descomprimido = descomprimir("booleanos.huff", "arbol.hufftree")
                with open("texto_descomprimido.txt", "w", encoding='utf-8') as f:
                    f.write(texto_descomprimido)
                print("Archivo descomprimido creado exitosamente: texto_descomprimido.txt")
                print("Texto descomprimido:", texto_descomprimido)
            except Exception as e:
                print(f"Error al descomprimir: {e}")

        elif opcion != 3:
            print("Opción inválida")

# -----------------------------------------------------------------------------
# Clase: TestHuffman
# Descripción: Pruebas unitarias para verificar el correcto funcionamiento del
#              compresor y descompresor de Huffman.
# -----------------------------------------------------------------------------
class TestHuffman(unittest.TestCase):
    def setUp(self):
        self.test_file = "test.txt"
        self.compressed_file = "booleanos.huff"
        self.tree_file = "arbol.hufftree"
        self.decompressed_file = "texto_descomprimido.txt"

    def test_empty_string(self):
        with open(self.test_file, "w", encoding='utf-8') as f:
            f.write("")
        texto = leer_archivo(self.test_file)
        huffman = comprimir(texto)
        with open(self.compressed_file, "wb") as f:
            huffman.tofile(f)
        texto_descomprimido = descomprimir(self.compressed_file, self.tree_file)
        self.assertEqual(texto_descomprimido, "", "La descompresión de una cadena vacía debería devolver una cadena vacía")

    def test_single_character(self):
        with open(self.test_file, "w", encoding='utf-8') as f:
            f.write("a")
        texto = leer_archivo(self.test_file)
        huffman = comprimir(texto)
        with open(self.compressed_file, "wb") as f:
            huffman.tofile(f)
        texto_descomprimido = descomprimir(self.compressed_file, self.tree_file)
        self.assertEqual(texto_descomprimido, "a", "La descompresión de un solo carácter debería devolver el mismo carácter")

    def test_typical_text(self):
        texto_original = "hello world"
        with open(self.test_file, "w", encoding='utf-8') as f:
            f.write(texto_original)
        texto = leer_archivo(self.test_file)
        huffman = comprimir(texto)
        with open(self.compressed_file, "wb") as f:
            huffman.tofile(f)
        texto_descomprimido = descomprimir(self.compressed_file, self.tree_file)
        self.assertEqual(texto_descomprimido, texto_original, "La descompresión debería devolver el texto original")

    def test_special_characters(self):
        texto_original = "hello\nworld\t !"
        with open(self.test_file, "w", encoding='utf-8') as f:
            f.write(texto_original)
        texto = leer_archivo(self.test_file)
        huffman = comprimir(texto)
        with open(self.compressed_file, "wb") as f:
            huffman.tofile(f)
        texto_descomprimido = descomprimir(self.compressed_file, self.tree_file)
        self.assertEqual(texto_descomprimido, texto_original, "La descompresión debería manejar caracteres especiales correctamente")

    def test_invalid_compressed_file(self):
        with open(self.test_file, "w", encoding='utf-8') as f:
            f.write("test")
        texto = leer_archivo(self.test_file)
        huffman = comprimir(texto)
        with open(self.compressed_file, "wb") as f:
            f.write(b"invalid")  # Escribir datos inválidos
        with self.assertRaises(Exception):
            descomprimir(self.compressed_file, self.tree_file)

if __name__ == "__main__":
    main()
    unittest.main(argv=[''], exit=False)