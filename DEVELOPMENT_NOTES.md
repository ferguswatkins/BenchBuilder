# BenchBuilder Development Notes

**Last Updated**: January 2025  
**Purpose**: Track development best practices, lessons learned, and technical decisions to maintain consistency and avoid repeated issues.

---

## 🚫 **AVOID - Components/Patterns That Cause Issues**

### **Material-UI Grid Component**
- **Issue**: Version compatibility problems, TypeScript errors with `item` prop
- **Problem**: Different MUI versions have incompatible Grid APIs (Grid vs Grid2)
- **Solution**: Use CSS Flexbox (`display: 'flex'`) or CSS Grid (`display: 'grid'`) instead
- **Example**:
  ```tsx
  // ❌ DON'T USE - Grid component
  <Grid container spacing={2}>
    <Grid item xs={12} sm={6}>
      <Component />
    </Grid>
  </Grid>

  // ✅ DO USE - CSS Flexbox/Grid
  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
    <Box sx={{ flex: '1 1 200px' }}>
      <Component />
    </Box>
  </Box>
  ```

---

## ✅ **PREFERRED - Reliable Patterns**

### **Layout Solutions**
1. **CSS Flexbox** for responsive rows/columns:
   ```tsx
   <Box sx={{
     display: 'flex',
     flexWrap: 'wrap',
     gap: 2,
     '& > *': { flex: '1 1 200px', minWidth: '200px' }
   }}>
   ```

2. **CSS Grid** for structured layouts:
   ```tsx
   <Box sx={{
     display: 'grid',
     gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
     gap: 3
   }}>
   ```

### **Component Structure**
- **Material-UI Box**: Reliable container for all layouts
- **Material-UI sx prop**: Consistent styling approach
- **Responsive breakpoints**: Use `{ xs: '...', md: '...' }` syntax

---

## 🎯 **ARCHITECTURE DECISIONS**

### **Frontend Stack**
- **React + TypeScript**: Type safety and modern development
- **Material-UI v5**: Component library (avoid Grid component)
- **CSS-in-JS**: Use `sx` prop for styling
- **API Integration**: Centralized service classes

### **Backend Stack**
- **FastAPI**: Python web framework
- **Pydantic**: Data validation and serialization
- **Yahoo Fantasy API**: External data source
- **VOR Algorithm**: Custom fantasy football value calculations

### **File Organization**
```
frontend/src/
├── components/     # Reusable UI components
├── pages/         # Route-level components
├── services/      # API integration
├── types/         # TypeScript definitions
└── utils/         # Helper functions
```

---

## 🔧 **DEVELOPMENT WORKFLOW**

### **Server Management**
- **USER RESPONSIBILITY**: The user will always start and manage servers
- **DO NOT**: Attempt to run `python main.py`, `npm start`, or any server commands
- **DO NOT**: Use `run_terminal_cmd` for server startup
- **REASON**: User prefers to control their development environment directly

### **Before Making Changes**
1. Check existing patterns in codebase
2. Avoid known problematic components (see AVOID section)
3. Use TypeScript strict mode
4. Test responsive behavior

### **Component Development**
1. Start with Material-UI Box for containers
2. Use CSS Flexbox/Grid for layouts
3. Implement responsive breakpoints
4. Add proper TypeScript types

### **API Integration**
1. Define types first in `types/index.ts`
2. Add service methods in `services/api.ts`
3. Handle loading/error states
4. Use React hooks for state management

---

## 📱 **RESPONSIVE DESIGN PATTERNS**

### **Breakpoints**
- `xs`: 0px+ (mobile)
- `sm`: 600px+ (small tablet)
- `md`: 900px+ (desktop)
- `lg`: 1200px+ (large desktop)

### **Common Responsive Patterns**
```tsx
// Responsive columns
gridTemplateColumns: { xs: '1fr', md: '1fr 1fr', lg: '1fr 1fr 1fr' }

// Responsive flex
flexDirection: { xs: 'column', md: 'row' }

// Responsive spacing
gap: { xs: 1, md: 2, lg: 3 }
```

---

## 🐛 **COMMON ISSUES & SOLUTIONS**

### **TypeScript Errors**
- **Issue**: Material-UI component prop conflicts
- **Solution**: Check component documentation, use simpler alternatives
- **Prevention**: Prefer native CSS properties over complex component APIs

### **Version Conflicts**
- **Issue**: Different MUI versions have breaking changes
- **Solution**: Use stable, well-documented patterns
- **Prevention**: Avoid cutting-edge features, stick to proven approaches

### **Performance Issues**
- **Issue**: Too many nested components
- **Solution**: Use CSS for layout instead of component nesting
- **Prevention**: Keep component trees shallow

---

## 🎨 **UI/UX STANDARDS**

### **Color Scheme**
- Primary: Blue (`#1976d2`)
- Secondary: Red (`#dc004e`)
- Success: Green (`#4caf50`)
- Warning: Orange (`#ff9800`)
- Error: Red (`#f44336`)

### **Spacing**
- Use Material-UI spacing units: `sx={{ mb: 3, p: 2 }}`
- Consistent gap sizes: 1, 2, 3 units

### **Typography**
- Headers: `variant="h4"`, `variant="h5"`, `variant="h6"`
- Body text: `variant="body1"`, `variant="body2"`
- Captions: `variant="caption"`

---

## 📝 **TESTING CHECKLIST**

### **Before Committing**
- [ ] TypeScript compiles without errors
- [ ] Component renders on mobile and desktop
- [ ] API calls handle loading/error states
- [ ] No console errors or warnings
- [ ] Responsive layout works correctly

### **Component Testing**
- [ ] Props are properly typed
- [ ] Event handlers work correctly
- [ ] Loading states display properly
- [ ] Error states are handled gracefully

---

## 🚀 **PERFORMANCE TIPS**

### **React Optimization**
- Use `useCallback` for event handlers
- Use `useMemo` for expensive calculations
- Avoid inline object creation in render

### **API Optimization**
- Implement proper loading states
- Cache API responses when appropriate
- Use parallel requests when possible
- Handle network errors gracefully

---

## 📚 **USEFUL RESOURCES**

- [Material-UI Documentation](https://mui.com/)
- [CSS Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [CSS Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
- [React TypeScript Best Practices](https://react-typescript-cheatsheet.netlify.app/)

---

## 🔄 **UPDATE PROCESS**

When you encounter new issues or find better solutions:

1. **Document the problem** in the AVOID section
2. **Add the solution** to the PREFERRED section  
3. **Update relevant code** to use the better approach
4. **Share knowledge** with the team

**Remember**: This file should be updated whenever we discover new patterns or encounter recurring issues!
