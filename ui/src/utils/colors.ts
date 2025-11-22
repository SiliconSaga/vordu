export const generateNeonColor = (seed: string): string => {
    let hash = 0;
    for (let i = 0; i < seed.length; i++) {
        hash = seed.charCodeAt(i) + ((hash << 5) - hash);
    }

    // Generate HSL
    // Hue: 0-360 based on hash
    const h = Math.abs(hash % 360);
    // Saturation: High (80-100%) for neon
    const s = 90 + (Math.abs(hash % 20) - 10);
    // Lightness: Medium-High (50-70%) for visibility against dark bg
    const l = 60 + (Math.abs(hash % 20) - 10);

    return `hsl(${h}, ${s}%, ${l}%)`;
};
