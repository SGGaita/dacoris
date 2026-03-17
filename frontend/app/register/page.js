'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Divider,
  Alert,
  CircularProgress,
  IconButton,
  Chip,
  Link as MuiLink
} from '@mui/material';
import { Science, Business, AttachMoney, Search, ArrowForward, School, LocalHospital, Public, AccountBalance } from '@mui/icons-material';
import { useTheme as useMuiTheme } from '@mui/material/styles';
import { COLORS } from '@/contexts/ThemeContext';

const ROLES = [
  'Researcher',
  'Grant Officer',
  'Finance Officer',
  'Research Administrator',
  'Data Steward',
  'IT/System Admin',
];

const INSTITUTIONS = [
  'University of Nairobi', 'Kenyatta University', 'KEMRI', 'Strathmore University',
  'Moi University', 'Egerton University', 'Maseno University', 'Other',
];

function passwordStrength(pw) {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score;
}

const PW_COLORS = ['#ef4444', '#f59e0b', '#14b8a6', '#34d399'];

// Network Canvas Component
function NetworkCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let nodes = [];
    let W = 0, H = 0, raf = 0;

    const resize = () => {
      W = canvas.width = canvas.offsetWidth;
      H = canvas.height = canvas.offsetHeight;
    };

    const init = () => {
      resize();
      nodes = Array.from({ length: 40 }, () => ({
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.4, vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 2.5 + 1,
        pulse: Math.random() * Math.PI * 2,
      }));
    };

    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      const t = Date.now() / 1000;

      for (let i = 0; i < nodes.length; i++) {
        const n = nodes[i];
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > W) n.vx *= -1;
        if (n.y < 0 || n.y > H) n.vy *= -1;

        for (let j = i + 1; j < nodes.length; j++) {
          const m = nodes[j];
          const dx = m.x - n.x, dy = m.y - n.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 110) {
            ctx.beginPath();
            ctx.moveTo(n.x, n.y);
            ctx.lineTo(m.x, m.y);
            ctx.strokeStyle = `rgba(28,167,161,${(1 - dist / 110) * 0.14})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }

        const glow = 0.5 + 0.5 * Math.sin(t * 1.5 + n.pulse);
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r + glow * 0.8, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(28,167,161,${0.3 + glow * 0.4})`;
        ctx.fill();
      }
      raf = requestAnimationFrame(draw);
    };

    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    init();
    draw();

    return () => {
      cancelAnimationFrame(raf);
      observer.disconnect();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
      }}
    />
  );
}

export default function SignupPage() {
  const router = useRouter();
  const theme = useMuiTheme();
  const [role, setRole] = useState('researcher');
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    organization: '',
    role: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const pwScore = passwordStrength(form.password);

  const handleChange = (field) => (e) => {
    setForm(f => ({ ...f, [field]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (pwScore < 2) {
      setError('Please choose a stronger password.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, role }),
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.message || 'Signup failed');
      }
      router.push('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: 'background.default', fontFamily: 'sans-serif', overflow: 'hidden' }}>
      
      {/* Left Panel */}
      <Box
        sx={{
          display: { xs: 'none', lg: 'flex' },
          width: '42%',
          flexShrink: 0,
          position: 'relative',
          bgcolor: 'background.paper',
          borderRight: 1,
          borderColor: 'divider',
          flexDirection: 'column',
          justifyContent: 'space-between',
          px: 6,
          py: 4,
          overflow: 'hidden',
        }}
      >
        <NetworkCanvas />

        {/* Main Content */}
        <Box sx={{ position: 'relative', zIndex: 10, flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <Typography variant="h2" sx={{ fontWeight: 700, mb: 2, lineHeight: 1.2, fontSize: { xs: '2rem', lg: '2.5rem' } }}>
            Join the DACORIS Platform
          </Typography>
          <Typography variant="h5" sx={{ color: 'primary.main', fontWeight: 600, mb: 4, fontSize: { xs: '1.25rem', lg: '1.5rem' } }}>
            Built for Research-Intensive Organizations
          </Typography>
          <Typography sx={{ fontSize: '1.125rem', color: 'text.secondary', lineHeight: 1.8, mb: 5 }}>
            Whether you're a university, hospital, NGO, or national institution, DACORIS gives your team the tools to govern research operations, manage grants end-to-end, steward your data responsibly, and report with confidence.
          </Typography>

          {/* Who It's For */}
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, color: 'text.primary' }}>
            Who It's For:
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mb: 5 }}>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
              <School sx={{ fontSize: 28, color: 'primary.main', mt: 0.5 }} />
              <Box>
                <Typography sx={{ fontSize: '1rem', fontWeight: 600, color: 'text.primary', mb: 0.5 }}>
                  Universities & Research Institutes
                </Typography>
                <Typography sx={{ fontSize: '0.875rem', color: 'text.secondary', lineHeight: 1.6 }}>
                  Full CRIS capabilities with ethics workflows and output tracking
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
              <LocalHospital sx={{ fontSize: 28, color: 'primary.main', mt: 0.5 }} />
              <Box>
                <Typography sx={{ fontSize: '1rem', fontWeight: 600, color: 'text.primary', mb: 0.5 }}>
                  Hospitals & Clinical Organizations
                </Typography>
                <Typography sx={{ fontSize: '0.875rem', color: 'text.secondary', lineHeight: 1.6 }}>
                  IRB/ethics management with HIPAA-aligned data controls
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
              <Public sx={{ fontSize: 28, color: 'primary.main', mt: 0.5 }} />
              <Box>
                <Typography sx={{ fontSize: '1rem', fontWeight: 600, color: 'text.primary', mb: 0.5 }}>
                  NGOs & Development Organizations
                </Typography>
                <Typography sx={{ fontSize: '0.875rem', color: 'text.secondary', lineHeight: 1.6 }}>
                  Grant lifecycle management from proposal to closeout
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
              <AccountBalance sx={{ fontSize: 28, color: 'primary.main', mt: 0.5 }} />
              <Box>
                <Typography sx={{ fontSize: '1rem', fontWeight: 600, color: 'text.primary', mb: 0.5 }}>
                  Government & Statistics Bureaus
                </Typography>
                <Typography sx={{ fontSize: '0.875rem', color: 'text.secondary', lineHeight: 1.6 }}>
                  Enterprise data integration, pipelines & analytics
                </Typography>
              </Box>
            </Box>
          </Box>

          {/* Trust Line */}
          <Typography sx={{ fontSize: '0.875rem', color: 'text.secondary', fontStyle: 'italic', lineHeight: 1.7 }}>
            Aligned with FAIR principles, GDPR standards, and internationally recognized research information frameworks.
          </Typography>
        </Box>
      </Box>

      {/* Right Panel - Form */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'center',
          py: 3,
          px: 2,
        }}
      >
        <Box sx={{ width: '100%', maxWidth: 450 }}>

          {/* Mobile logo */}
          <Box sx={{ display: { xs: 'flex', lg: 'none' }, alignItems: 'center', gap: 1, mb: 3 }}>
            <Box sx={{ width: 32, height: 32, bgcolor: 'primary.main', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 12, color: '#fff' }}>
              DC
            </Box>
            <Typography sx={{ fontWeight: 'bold', fontSize: 14, letterSpacing: 2, color: 'text.primary' }}>
              DACORIS
            </Typography>
          </Box>

          <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
            Create Your Account
          </Typography>
          <Typography sx={{ fontSize: '0.875rem', color: 'text.secondary', mb: 4 }}>
            Set up your organization's DACORIS workspace
          </Typography>

          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>

            {/* Full Name */}
            <Box>
              <Typography variant="overline" sx={{ mb: 1, display: 'block', color: 'text.secondary' }}>
                Full Name
              </Typography>
              <TextField
                fullWidth
                placeholder="Dr. Amina Wanjiku"
                required
                value={form.fullName}
                onChange={handleChange('fullName')}
              />
            </Box>

            {/* Email */}
            <Box>
              <Typography variant="overline" sx={{ mb: 1, display: 'block', color: 'text.secondary' }}>
                Institutional Email
              </Typography>
              <TextField
                fullWidth
                type="email"
                placeholder="a.wanjiku@university.ac.ke"
                required
                value={form.email}
                onChange={handleChange('email')}
              />
            </Box>

            {/* Organization Name */}
            <Box>
              <Typography variant="overline" sx={{ mb: 1, display: 'block', color: 'text.secondary' }}>
                Organization Name
              </Typography>
              <TextField
                fullWidth
                placeholder="University of Nairobi"
                required
                value={form.organization}
                onChange={handleChange('organization')}
              />
            </Box>

            {/* Role */}
            <Box>
              <Typography variant="overline" sx={{ mb: 1, display: 'block', color: 'text.secondary' }}>
                Role
              </Typography>
              <FormControl fullWidth required>
                <Select
                  value={form.role}
                  onChange={handleChange('role')}
                  displayEmpty
                >
                  <MenuItem value="" disabled>
                    Select your primary role
                  </MenuItem>
                  {ROLES.map(r => (
                    <MenuItem key={r} value={r}>{r}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary', mt: 1, fontStyle: 'italic' }}>
                Select your primary role: Researcher · Grant Officer · Finance Officer · Research Administrator · Data Steward · IT/System Admin
              </Typography>
            </Box>

            {/* Password */}
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="overline" sx={{ mb: 1, display: 'block', color: 'text.secondary' }}>
                  Password
                </Typography>
                <TextField
                  fullWidth
                  type="password"
                  placeholder="Min. 8 characters"
                  required
                  value={form.password}
                  onChange={handleChange('password')}
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="overline" sx={{ mb: 1, display: 'block', color: 'text.secondary' }}>
                  Confirm Password
                </Typography>
                <TextField
                  fullWidth
                  type="password"
                  placeholder="Re-enter password"
                  required
                  value={form.confirmPassword}
                  onChange={handleChange('confirmPassword')}
                />
              </Grid>
            </Grid>
            {form.password && (
              <Box>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  {[0, 1, 2, 3].map(i => (
                    <Box
                      key={i}
                      sx={{
                        height: 4,
                        flex: 1,
                        borderRadius: 999,
                        transition: 'all 0.3s',
                        bgcolor: i < pwScore ? PW_COLORS[Math.min(pwScore - 1, 3)] : 'divider',
                      }}
                    />
                  ))}
                </Box>
                <Typography sx={{ fontSize: '0.75rem', mt: 1, color: PW_COLORS[Math.min(pwScore - 1, 3)] || 'text.secondary' }}>
                  {['Too weak', 'Weak', 'Fair', 'Strong'][pwScore - 1] || 'Enter a password'}
                </Typography>
              </Box>
            )}

            {/* Error */}
            {error && (
              <Alert severity="error">
                {error}
              </Alert>
            )}

            {/* Submit */}
            {/* Consent Note */}
            <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary', lineHeight: 1.7, fontStyle: 'italic', p: 2, bgcolor: 'action.hover', borderRadius: 1, border: 1, borderColor: 'divider' }}>
              By registering, you agree to DACORIS's data processing terms. Your institutional data is stored securely with role-based access controls and full audit logging.
            </Typography>

            {/* Submit */}
            <Button
              type="submit"
              disabled={loading}
              fullWidth
              variant="contained"
              color="primary"
              sx={{ py: 2 }}
            >
              {loading ? (
                <CircularProgress size={16} sx={{ color: 'inherit' }} />
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                  Create Account <ArrowForward sx={{ fontSize: 16 }} />
                </Box>
              )}
            </Button>

            {/* Bottom CTA */}
            <Box sx={{ textAlign: 'center', mt: 3, pt: 3, borderTop: 1, borderColor: 'divider' }}>
              <Typography sx={{ fontSize: '0.875rem', color: 'text.secondary' }}>
                Already have an account?{' '}
                <MuiLink component={Link} href="/login" sx={{ color: 'primary.main', fontWeight: 600, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
                  Sign in →
                </MuiLink>
              </Typography>
            </Box>

          </Box>
        </Box>
      </Box>
    </Box>
  );
}
