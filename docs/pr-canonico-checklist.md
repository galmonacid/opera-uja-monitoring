# Checklist de coordinación de PRs

## PR canónico seleccionado
- **Canónico**: PR con `asset=all` + modo de lectura en mapa.

## Acciones inmediatas
1. Marcar todos los PRs no canónicos con etiqueta **`do not merge`** (o comentario equivalente temporal).
2. En cada PR no canónico, publicar el comentario:
   - `Este PR queda superseded por #<PR_CANONICO>`
3. Congelar pushes en ramas antiguas hasta que el PR canónico se cierre.

## Comandos sugeridos (GitHub CLI)
> Reemplazar `<OWNER/REPO>`, `<PR_CANONICO>` y la lista de PRs no canónicos.

```bash
# 1) Etiquetar PRs no canónicos
for pr in 12 13 14; do
  gh pr edit "$pr" --repo <OWNER/REPO> --add-label "do not merge"
done

# 2) Comentar PRs no canónicos como superseded
for pr in 12 13 14; do
  gh pr comment "$pr" --repo <OWNER/REPO> \
    --body "Este PR queda superseded por #<PR_CANONICO>"
done
```

## Estado
- [ ] PR canónico identificado
- [ ] PRs no canónicos etiquetados
- [ ] Comentarios `superseded` publicados
- [ ] Pushes congelados en ramas antiguas
