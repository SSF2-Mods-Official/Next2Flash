package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class AuraLaserBeam_117 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var self:*;

        public function AuraLaserBeam_117()
        {
            super();
            addFrameScript(0, this.frame1, 11, this.frame12, 12, this.frame13, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
        }

        internal function frame12():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame13():*
        {
            this.self.updateAttackStats({"refreshRate":999});
            this.self.updateAttackBoxStats(1, {
                "damage":14,
                "direction":40,
                "power":40,
                "kbConstant":120,
                "hitStun":10,
                "selfHitStun":0,
                "hitLag":-1,
                "effectSound":"brawl_fire_l",
                "camShake":12
            });
            this.self.refreshAttackID();
        }

        internal function frame24():*
        {
            this.self.destroy();
        }


    }
}

