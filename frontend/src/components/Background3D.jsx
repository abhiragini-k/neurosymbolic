import { useEffect, useRef } from 'react';
import * as THREE from 'three';

const Background3D = () => {
    const containerRef = useRef(null);

    useEffect(() => {
        if (!containerRef.current) return;

        // --- Configuration ---
        const CONFIG = {
            particleCount: 180,
            connectionDistance: 130,
            baseColor: 0x0099aa, // Darker Cyan/Teal for white background
            accentColor: 0x4400aa, // Darker Purple for white background
            bgColor: 0xffffff, // White
            rotationSpeed: 0.001
        };

        // --- Init Scene ---
        const container = containerRef.current;
        const scene = new THREE.Scene();
        // Removed fog for better contrast on white
        scene.background = new THREE.Color(CONFIG.bgColor);

        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 400;

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);

        // --- Create Particles (Nodes) ---
        const particlesGeometry = new THREE.BufferGeometry();
        const particlePositions = new Float32Array(CONFIG.particleCount * 3);
        const particleVelocities = []; // Store velocity for independent movement

        const r = 500; // Radius of the cloud
        for (let i = 0; i < CONFIG.particleCount; i++) {
            // Random position inside a sphere
            const x = Math.random() * r - r / 2;
            const y = Math.random() * r - r / 2;
            const z = Math.random() * r - r / 2;

            particlePositions[i * 3] = x;
            particlePositions[i * 3 + 1] = y;
            particlePositions[i * 3 + 2] = z;

            // Give each particle a tiny random drift velocity
            particleVelocities.push({
                x: (Math.random() - 0.5) * 0.2,
                y: (Math.random() - 0.5) * 0.2,
                z: (Math.random() - 0.5) * 0.2
            });
        }

        particlesGeometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

        // Material for the nodes (Glowing Dots)
        const particlesMaterial = new THREE.PointsMaterial({
            color: CONFIG.baseColor,
            size: 4,
            transparent: true,
            opacity: 0.9,
            blending: THREE.NormalBlending,
            sizeAttenuation: true
        });

        const particleSystem = new THREE.Points(particlesGeometry, particlesMaterial);
        scene.add(particleSystem);

        // --- Create Connections (Edges) ---
        // We will update the geometry of lines every frame based on particle proximity
        const linesGeometry = new THREE.BufferGeometry();
        const linesMaterial = new THREE.LineBasicMaterial({
            color: CONFIG.accentColor,
            transparent: true,
            opacity: 0.4,
            blending: THREE.NormalBlending
        });

        const linesMesh = new THREE.LineSegments(linesGeometry, linesMaterial);
        scene.add(linesMesh);

        // --- Create a "Core" Geometry (Symbolic/Drug Representation) ---
        // A wireframe Icosahedron spinning in the center to represent the core model
        const coreGeometry = new THREE.IcosahedronGeometry(60, 1);
        const coreMaterial = new THREE.MeshBasicMaterial({
            color: CONFIG.baseColor,
            wireframe: true,
            transparent: true,
            opacity: 0.15
        });
        const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial);
        scene.add(coreMesh);

        // --- Dynamic Line Drawing ---
        const updateLines = (positions) => {
            const linePositions = [];

            // Note: This is O(N^2) complexity. 
            // Kept particle count low (180) to ensure high FPS on all devices.

            for (let i = 0; i < CONFIG.particleCount; i++) {
                const x1 = positions[i * 3];
                const y1 = positions[i * 3 + 1];
                const z1 = positions[i * 3 + 2];

                for (let j = i + 1; j < CONFIG.particleCount; j++) {
                    const x2 = positions[j * 3];
                    const y2 = positions[j * 3 + 1];
                    const z2 = positions[j * 3 + 2];

                    const dist = Math.sqrt(
                        (x1 - x2) ** 2 +
                        (y1 - y2) ** 2 +
                        (z1 - z2) ** 2
                    );

                    if (dist < CONFIG.connectionDistance) {
                        // Add vertices for the line segment
                        linePositions.push(x1, y1, z1);
                        linePositions.push(x2, y2, z2);
                    }
                }
            }

            linesMesh.geometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
        };

        // --- Animation Loop ---
        let time = 0;
        let animationFrameId;

        const animate = () => {
            animationFrameId = requestAnimationFrame(animate);

            time += 0.005;

            // 1. Rotate the whole system slowly
            particleSystem.rotation.y += CONFIG.rotationSpeed;
            linesMesh.rotation.y += CONFIG.rotationSpeed;

            // 2. Animate the Core
            coreMesh.rotation.x -= 0.002;
            coreMesh.rotation.y -= 0.002;
            // Pulsing effect
            const scale = 1 + Math.sin(time) * 0.1;
            coreMesh.scale.set(scale, scale, scale);

            // 3. Update Particle Positions (Drift)
            const positions = particleSystem.geometry.attributes.position.array;

            for (let i = 0; i < CONFIG.particleCount; i++) {
                // Update position based on velocity
                positions[i * 3] += particleVelocities[i].x;
                positions[i * 3 + 1] += particleVelocities[i].y;
                positions[i * 3 + 2] += particleVelocities[i].z;

                // Boundary check: if too far, reverse velocity
                if (Math.abs(positions[i * 3]) > r / 2) particleVelocities[i].x *= -1;
                if (Math.abs(positions[i * 3 + 1]) > r / 2) particleVelocities[i].y *= -1;
                if (Math.abs(positions[i * 3 + 2]) > r / 2) particleVelocities[i].z *= -1;
            }
            particleSystem.geometry.attributes.position.needsUpdate = true;

            // 4. Update Lines (The GNN logic)
            updateLines(positions);

            // Render
            renderer.render(scene, camera);
        };

        animate();

        // --- Interaction (Mouse Parallax) ---
        const handleMouseMove = (event) => {
            const mouseX = (event.clientX / window.innerWidth) * 2 - 1;
            const mouseY = -(event.clientY / window.innerHeight) * 2 + 1;

            // Gentle camera movement
            camera.position.x += (mouseX * 100 - camera.position.x) * 0.05;
            camera.position.y += (mouseY * 100 - camera.position.y) * 0.05;
            camera.lookAt(scene.position);
        };
        window.addEventListener('mousemove', handleMouseMove);

        // --- Resize Handler ---
        const handleResize = () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        };
        window.addEventListener('resize', handleResize);

        // Cleanup
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('resize', handleResize);
            cancelAnimationFrame(animationFrameId);

            if (container && renderer.domElement) {
                container.removeChild(renderer.domElement);
            }

            // Dispose Three.js resources
            particlesGeometry.dispose();
            particlesMaterial.dispose();
            linesGeometry.dispose();
            linesMaterial.dispose();
            coreGeometry.dispose();
            coreMaterial.dispose();
            renderer.dispose();
        };
    }, []);

    return (
        <div
            ref={containerRef}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                zIndex: 0,
                outline: 'none',
                pointerEvents: 'none' // Let clicks pass through if needed, though new.html had it on canvas-container which was behind overlay
            }}
        />
    );
};

export default Background3D;
