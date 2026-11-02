import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material'

interface Props {
  title: string
  message: string
  confirmLabel: string
  pending?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({ title, message, confirmLabel, pending, onConfirm, onCancel }: Props) {
  return (
    <Dialog open onClose={onCancel} maxWidth="xs" fullWidth>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <DialogContentText>{message}</DialogContentText>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onCancel}>Cancel</Button>
        <Button variant="contained" onClick={onConfirm} disabled={pending}>
          {confirmLabel}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
