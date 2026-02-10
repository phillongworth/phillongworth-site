/**
 * Shared Leaflet configuration for phillongworth-site
 *
 * Provides common base map tile layers and utility functions
 * for consistent map appearance across all pages.
 *
 * Usage:
 *   <script src="shared/js/leaflet-config.js"></script>
 *   <script>
 *     const map = L.map('map').setView([53.7, -1.9], 12);
 *     LeafletConfig.addDefaultBaseLayer(map);
 *     // Or use layer switcher: LeafletConfig.addLayerControl(map);
 *   </script>
 */

const LeafletConfig = (function() {
    'use strict';

    // Base map tile layer definitions
    const baseMaps = {
        osm: {
            name: 'OpenStreetMap',
            layer: function() {
                return L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
                    maxZoom: 19
                });
            }
        },
        topo: {
            name: 'OpenTopoMap',
            layer: function() {
                return L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
                    maxZoom: 17
                });
            }
        },
        cycle: {
            name: 'CyclOSM',
            layer: function() {
                return L.tileLayer('https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.cyclosm.org">CyclOSM</a> &copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
                    maxZoom: 20
                });
            }
        },
        esriSat: {
            name: 'Satellite',
            layer: function() {
                return L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                    attribution: '&copy; <a href="https://www.esri.com">Esri</a> &mdash; Sources: Esri, Maxar, Earthstar Geographics',
                    maxZoom: 19
                });
            }
        },
        hybrid: {
            name: 'Satellite + Roads',
            layer: function() {
                return L.layerGroup([
                    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                        attribution: '&copy; <a href="https://www.esri.com">Esri</a>',
                        maxZoom: 19
                    }),
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
                        maxZoom: 19,
                        opacity: 0.4
                    })
                ]);
            }
        }
    };

    // Common map centers for the region
    const centers = {
        calderdale: [53.765, -1.99],
        kirklees: [53.60, -1.85],
        default: [53.72, -1.93]
    };

    // Default zoom levels
    const defaultZoom = 12;

    /**
     * Add the default OpenStreetMap base layer to a map
     * @param {L.Map} map - Leaflet map instance
     * @returns {L.TileLayer} The added tile layer
     */
    function addDefaultBaseLayer(map) {
        const layer = baseMaps.osm.layer();
        layer.addTo(map);
        return layer;
    }

    /**
     * Create a Leaflet layers control with all base maps
     * @param {L.Map} map - Leaflet map instance
     * @param {string} defaultLayer - Key of the default layer (default: 'osm')
     * @returns {L.Control.Layers} The layers control
     */
    function addLayerControl(map, defaultLayer) {
        defaultLayer = defaultLayer || 'osm';

        const baseLayerControl = {};
        for (const key in baseMaps) {
            baseLayerControl[baseMaps[key].name] = baseMaps[key].layer();
        }

        // Add default layer to map
        if (baseMaps[defaultLayer]) {
            baseMaps[defaultLayer].layer().addTo(map);
        }

        return L.control.layers(baseLayerControl, null, { position: 'topright' }).addTo(map);
    }

    /**
     * Get a specific base map layer
     * @param {string} key - Layer key (osm, topo, cycle, esriSat, hybrid)
     * @returns {L.TileLayer|L.LayerGroup} The tile layer
     */
    function getBaseLayer(key) {
        if (baseMaps[key]) {
            return baseMaps[key].layer();
        }
        return baseMaps.osm.layer();
    }

    // Public API
    return {
        baseMaps: baseMaps,
        centers: centers,
        defaultZoom: defaultZoom,
        addDefaultBaseLayer: addDefaultBaseLayer,
        addLayerControl: addLayerControl,
        getBaseLayer: getBaseLayer
    };
})();
