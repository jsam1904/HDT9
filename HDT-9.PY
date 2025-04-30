from bitarray import bitarray

print("Compresor HUFFMAN")
#contador de frecuencias

def frecuencia(texto):
    frecuencias = {}
    for caracter in texto:
        if caracter in frecuencias:
            frecuencias[caracter] += 1
        else:
            frecuencias[caracter] = 1
    return frecuencias

def crear_nodo(frecuencias):
    nodos = []
    for caracter, frecuencia in frecuencias.items():
        nodos.append((frecuencia, bitarray(), caracter))
    return nodos

def crear_arbol(nodos):
    while len(nodos) > 1:
        nodos.sort(key=lambda x: x[0])  
        izquierda = nodos.pop(0)  
        derecha = nodos.pop(0)  
        nuevo_nodo = (izquierda[0] + derecha[0], (izquierda, derecha), None)
        nodos.append(nuevo_nodo)  
    with open("arbol.hufftree", "w") as f:
        for nodo in nodos:
            f.write(f"{nodo[0]} {nodo[1]} {nodo[2]}\n")
    return nodos[0]