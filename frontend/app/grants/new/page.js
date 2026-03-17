'use client';

import { useState } from 'react';
import { Box, Typography, TextField, Button, Card, CardContent, Grid, MenuItem } from '@mui/material';
import { Save, ArrowBack } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import AppShell from '@/components/layout/AppShell';
import { grantsAPI } from '@/lib/apiModules';

export default function NewOpportunityPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: '',
    sponsor: '',
    description: '',
    category: '',
    geography: '',
    applicant_type: '',
    funding_type: '',
    amount_min: '',
    amount_max: '',
    currency: 'KES',
    open_date: '',
    deadline: '',
  });
  const [saving, setSaving] = useState(false);

  const handleChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const response = await grantsAPI.createOpportunity({
        ...formData,
        amount_min: formData.amount_min ? parseFloat(formData.amount_min) : null,
        amount_max: formData.amount_max ? parseFloat(formData.amount_max) : null,
      });
      router.push(`/grants/${response.data.id}`);
    } catch (error) {
      console.error('Failed to create opportunity:', error);
      alert('Failed to create opportunity');
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppShell currentModule="grants">
      <Box>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => router.back()}
          sx={{ mb: 2 }}
        >
          Back
        </Button>

        <Typography variant="h4" fontWeight={700} gutterBottom>
          Create Grant Opportunity
        </Typography>

        <Card sx={{ mt: 3 }}>
          <CardContent>
            <form onSubmit={handleSubmit}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Title"
                    required
                    value={formData.title}
                    onChange={handleChange('title')}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Sponsor"
                    value={formData.sponsor}
                    onChange={handleChange('sponsor')}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Category"
                    value={formData.category}
                    onChange={handleChange('category')}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    multiline
                    rows={4}
                    value={formData.description}
                    onChange={handleChange('description')}
                  />
                </Grid>

                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Minimum Amount"
                    type="number"
                    value={formData.amount_min}
                    onChange={handleChange('amount_min')}
                  />
                </Grid>

                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Maximum Amount"
                    type="number"
                    value={formData.amount_max}
                    onChange={handleChange('amount_max')}
                  />
                </Grid>

                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    select
                    label="Currency"
                    value={formData.currency}
                    onChange={handleChange('currency')}
                  >
                    <MenuItem value="KES">KES</MenuItem>
                    <MenuItem value="USD">USD</MenuItem>
                    <MenuItem value="EUR">EUR</MenuItem>
                    <MenuItem value="GBP">GBP</MenuItem>
                  </TextField>
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Open Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    value={formData.open_date}
                    onChange={handleChange('open_date')}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Deadline"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    value={formData.deadline}
                    onChange={handleChange('deadline')}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Geography"
                    value={formData.geography}
                    onChange={handleChange('geography')}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Applicant Type"
                    value={formData.applicant_type}
                    onChange={handleChange('applicant_type')}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Funding Type"
                    value={formData.funding_type}
                    onChange={handleChange('funding_type')}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                    <Button
                      variant="outlined"
                      onClick={() => router.back()}
                      disabled={saving}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      variant="contained"
                      startIcon={<Save />}
                      disabled={saving}
                    >
                      {saving ? 'Creating...' : 'Create Opportunity'}
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </form>
          </CardContent>
        </Card>
      </Box>
    </AppShell>
  );
}
