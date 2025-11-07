import pandas as pd
from typing import List, Union, Optional
from collections import Counter
import re

class DataFilterManager:
    """
    Gestor de flujo de trabajo para filtrado de DataFrames con jerarquía de subsets.
    
    Permite crear, analizar y gestionar múltiples subsets de un DataFrame principal
    con eliminaciones propagadas automáticamente a los subsets padres.
    Además, guarda un historial de cambios para deshacer operaciones.
    
    Attributes
    ----------
    df_original : pd.DataFrame
        Copia original del DataFrame base (para restaurar todo).
    df_principal : pd.DataFrame
        DataFrame base que se modifica al aplicar filtros.
    columna_id : str
        Nombre de la columna identificadora usada para match exacto.
    subsets : dict
        Diccionario que almacena los subsets creados.
    _historial_principal : list
        Pila que guarda copias del df_principal antes de cada eliminación.
    """
    
    def __init__(self, df: pd.DataFrame, columna_id: str):
        self.df_original = df.copy()
        self.df_principal = df.copy()
        self.columna_id = columna_id
        self.subsets = {'principal': self.df_principal}
        self._historial_principal = []  # Para restaurar_anterior()
    
    def restaurar_anterior(self) -> None:
        """
        Deshace la ULTIMA operación de eliminación (aplicar_filtro).
        Restaura el df_principal a su estado inmediatamente anterior.
        
        Returns
        -------
        None
            Modifica self.df_principal in-place.
        """
        if not self._historial_principal:
            print("⚠️ No hay operaciones para deshacer.")
            return
        
        # Recuperar el último estado guardado
        self.df_principal = self._historial_principal.pop()
        self.subsets['principal'] = self.df_principal
        
        print(f"✅ Restaurado al estado anterior. "
              f"df_principal ahora tiene {len(self.df_principal)} filas.")
    
    def restaurar_todo(self) -> None:
        """
        Restaura el DataFrame principal a su estado ORIGINAL (al crear el objeto).
        Limpia todo el historial de cambios y elimina todos los subsets.
        
        Returns
        -------
        None
            Modifica self.df_principal in-place y limpia todo.
        """
        self.df_principal = self.df_original.copy()
        self.subsets = {'principal': self.df_principal}
        self._historial_principal.clear()
        
        print("✅ DataFrame principal restaurado al estado ORIGINAL.")
        print("✅ Historial de cambios limpiado.")
        print("✅ Todos los subsets eliminados.")
    
    def filtrar_por_palabra(
        self, 
        columna: str, 
        palabras: Union[str, List[str]], 
        nombre: str,
        condicional: str = 'OR',
        case_sensitive: bool = False,
        match_exacto: bool = False,
        usar_principal: bool = True,
        parent: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Crea un subset filtrando por palabras clave.
        
        Parameters
        ----------
        parent : str, optional
            Nombre del subset padre. Usado internamente por `filtrar_subset()`.
        """
        if nombre in self.subsets:
            raise ValueError(f"El subset '{nombre}' ya existe. Usa otro nombre o elimínalo primero.")
        
        df_origen = self.df_principal if usar_principal else self.subsets.get('ultimo', self.df_principal)
        
        subset = filtro_palabras(
            df=df_origen,
            columna_descripcion=columna,
            palabras=palabras,
            condicional=condicional,
            case_sensitive=case_sensitive,
            match_exacto=match_exacto
        )
        
        self.subsets[nombre] = subset
        subset._parent = parent  # Track parent
        self.subsets['ultimo'] = subset
        
        print(f"✅ Subset '{nombre}' creado con {len(subset)} filas")
        if parent:
            print(f"   └─ Hijo de '{parent}'")
        return subset
    
    def ver_top_palabras(
        self, 
        nombre_subset: Optional[str] = 'principal', 
        top_n: int = 10, 
        excluir_palabras: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Muestra el top de palabras más frecuentes del DataFrame principal o de un subset.
        
        Parameters
        ----------
        nombre_subset : str, optional
            Nombre del subset a analizar. Por defecto 'principal'.
        """
        if nombre_subset not in self.subsets:
            raise KeyError(f"Subset '{nombre_subset}' no encontrado. Usa listar_subsets() para ver disponibles.")
        
        df_analizar = self.subsets[nombre_subset]
        nombre_mostrar = nombre_subset
        
        df_top = top_palabras(
            df=df_analizar,
            columna_descripcion='descripcion',
            top_n=top_n,
            excluir_palabras=excluir_palabras
        )
        
        print(f"\n--- Top {top_n} palabras en '{nombre_mostrar}' ---")
        print(df_top.to_string(index=False))
        return df_top
    
    def agregar_excluidos(
        self, 
        nombre_subset: str, 
        palabras: List[str]
    ) -> None:
        """
        Agrega palabras a la lista de exclusión para un subset existente.
        """
        if nombre_subset not in self.subsets:
            raise KeyError(f"Subset '{nombre_subset}' no encontrado.")
        
        if not hasattr(self.subsets[nombre_subset], '_palabras_excluidas'):
            self.subsets[nombre_subset]._palabras_excluidas = []
        
        self.subsets[nombre_subset]._palabras_excluidas.extend(palabras)
        print(f"✅ Palabras excluidas agregadas a '{nombre_subset}': {palabras}")
    
    def filtrar_subset(
        self, 
        nombre_origen: str,
        columna: str,
        palabras: Union[str, List[str]],
        nombre: str,
        condicional: str = 'OR',
        case_sensitive: bool = False,
        match_exacto: bool = False
    ) -> pd.DataFrame:
        """
        Crea un subset a partir de filtrar otro subset existente.
        
        Parameters
        ----------
        nombre_origen : str
            Nombre del subset fuente para el filtrado.
        columna, palabras, nombre, condicional, case_sensitive, match_exacto
            Parámetros de filtrado (ver filtrar_por_palabra).
            
        Returns
        -------
        pd.DataFrame
            El nuevo subset creado, con relación padre-hijo establecida.
        """
        if nombre_origen not in self.subsets:
            raise KeyError(f"Subset fuente '{nombre_origen}' no encontrado.")
        
        df_origen_guardado = self.df_principal
        self.df_principal = self.subsets[nombre_origen]
        
        try:
            resultado = self.filtrar_por_palabra(
                columna=columna,
                palabras=palabras,
                nombre=nombre,
                condicional=condicional,
                case_sensitive=case_sensitive,
                match_exacto=match_exacto,
                usar_principal=True,
                parent=nombre_origen  # Establecer relación padre-hijo
            )
        finally:
            self.df_principal = df_origen_guardado
        
        return resultado
    
    def aplicar_filtro(self, nombre_subset: str, propagar_a_padre: bool = True) -> None:
        """
        ELIMINA las filas del subset especificado del DataFrame principal
        Y opcionalmente del subset padre (si existe).
        
        Parameters
        ----------
        nombre_subset : str
            Nombre del subset cuyas filas se eliminarán.
        propagar_a_padre : bool, optional
            Si True, elimina también las filas del subset padre. Por defecto True.
            
        Returns
        -------
        None
            Modifica self.df_principal in-place y el subset padre si aplica.
        """
        if nombre_subset not in self.subsets:
            raise KeyError(f"Subset '{nombre_subset}' no encontrado.")
        
        subset = self.subsets[nombre_subset]
        
        if subset.empty:
            print(f"⚠️ Subset '{nombre_subset}' está vacío. No se eliminó nada.")
            return
        
        # --- GUARDAR ESTADO ANTERIOR EN EL HISTORIAL ---
        self._historial_principal.append(self.df_principal.copy())
        
        # 1. Eliminar del principal
        self.df_principal = drop_lines_key(
            df_target=self.df_principal,
            df_reference=subset,
            column_key=self.columna_id
        )
        self.subsets['principal'] = self.df_principal
        
        print(f"✅ Eliminadas {len(subset)} filas del df_principal. "
              f"Quedan {len(self.df_principal)} filas.")
        
        # 2. Si tiene padre y propagar_a_padre=True, eliminar también del padre
        if propagar_a_padre and hasattr(subset, '_parent') and subset._parent:
            parent_name = subset._parent
            if parent_name in self.subsets:
                parent_df_original = self.subsets[parent_name].copy()
                
                self.subsets[parent_name] = drop_lines_key(
                    df_target=self.subsets[parent_name],
                    df_reference=subset,
                    column_key=self.columna_id
                )
                
                filas_eliminadas = len(parent_df_original) - len(self.subsets[parent_name])
                if filas_eliminadas > 0:
                    print(f"✅ Eliminadas {filas_eliminadas} filas del subset padre '{parent_name}'. "
                          f"Quedan {len(self.subsets[parent_name])} filas.")
                else:
                    print(f"ℹ️ No se eliminaron filas del subset padre '{parent_name}'.")
        
        # Marcar el subset como "aplicado"
        self.subsets[nombre_subset]._aplicado = True
    
    def get_principal(self) -> pd.DataFrame:
        """
        Obtiene el DataFrame principal actual (después de aplicar filtros).
        
        Returns
        -------
        pd.DataFrame
            Copia del DataFrame principal en su estado actual.
        """
        return self.df_principal.copy()
    
    def listar_subsets(self) -> None:
        """
        Muestra todos los subsets creados con su cantidad de filas y relaciones.
        """
        print("\n--- Subsets disponibles ---")
        if not self.subsets:
            print("No hay subsets creados.")
            return
        
        # Mostrar principal primero
        print(f"  'principal' (df_principal): {len(self.df_principal)} filas")
        
        # Mostrar otros subsets con relación padre
        for nombre, subset in self.subsets.items():
            if nombre not in ['principal', 'ultimo']:
                parent = getattr(subset, '_parent', None)
                parent_info = f" └─ Hijo de '{parent}'" if parent else ""
                print(f"  '{nombre}': {len(subset)} filas{parent_info}")
    
    def get_subset(self, nombre: str) -> pd.DataFrame:
        """
        Obtiene un subset específico o el principal.
        
        Parameters
        ----------
        nombre : str
            Nombre del subset a obtener. Puede ser 'principal'.
            
        Returns
        -------
        pd.DataFrame
            El subset solicitado.
        """
        if nombre not in self.subsets:
            raise KeyError(f"Subset '{nombre}' no encontrado.")
        return self.subsets[nombre].copy()
