'use client';

import { useState, useEffect } from 'react';
import { Box, Typography, Grid, Card, CardContent, CardActionArea } from '@mui/material';
import { Assessment, Science, Storage, TrendingUp } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import AppShell from '@/components/layout/AppShell';

export default function DashboardPage() {
  const router = useRouter();

  const modules = [
    {
      title: 'Grants',
      icon: <Assessment sx={{ fontSize: 48 }} />,
      description: 'Manage grant opportunities, proposals, and awards',
      path: '/grants',
      color: '#1e3a8a',
    },
    {
      title: 'Research',
      icon: <Science sx={{ fontSize: 48 }} />,
      description: 'Track research projects and ethics applications',
      path: '/research',
      color: '#1ca7a1',
    },
    {
      title: 'Data Capture',
      icon: <Storage sx={{ fontSize: 48 }} />,
      description: 'Create forms and collect research data',
      path: '/data',
      color: '#059669',
    },
  ];

  return (
    <AppShell currentModule="dashboard">
      <Box>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Welcome to DACORIS - Your Research Management System
        </Typography>

        <Grid container spacing={3}>
          {modules.map((module) => (
            <Grid item xs={12} md={4} key={module.path}>
              <Card 
                sx={{ 
                  height: '100%',
                  '&:hover': { 
                    boxShadow: 6,
                    transform: 'translateY(-4px)',
                    transition: 'all 0.3s ease'
                  }
                }}
              >
                <CardActionArea 
                  onClick={() => router.push(module.path)}
                  sx={{ height: '100%', p: 3 }}
                >
                  <CardContent>
                    <Box 
                      sx={{ 
                        display: 'flex', 
                        justifyContent: 'center', 
                        mb: 2,
                        color: module.color
                      }}
                    >
                      {module.icon}
                    </Box>
                    <Typography 
                      variant="h5" 
                      fontWeight={600} 
                      textAlign="center" 
                      gutterBottom
                    >
                      {module.title}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      textAlign="center"
                    >
                      {module.description}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mt: 6 }}>
          <Typography variant="h5" fontWeight={600} gutterBottom>
            Quick Stats
          </Typography>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Assessment color="primary" />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        0
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Active Grants
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Science color="secondary" />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        0
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Research Projects
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Storage color="success" />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        0
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Data Forms
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <TrendingUp color="warning" />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        0
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Submissions
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </AppShell>
  );
}
