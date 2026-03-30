package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class FlareProjectile_179 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var self:*;

        public function FlareProjectile_179()
        {
            super();
            addFrameScript(0, this.frame1, 30, this.frame31, 55, this.frame56, 97, this.frame98);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAttackStats({"refreshRate":1});
                this.self.addToCamera();
            };
        }

        internal function frame31():*
        {
            this.self.updateAttackStats({"refreshRate":999});
            this.self.updateAttackBoxStats(1, {
                "hasEffect":true,
                "damage":26,
                "hitStun":6,
                "selfHitStun":6,
                "direction":30,
                "power":90,
                "kbConstant":100,
                "effectSound":"brawl_bomb_l",
                "effect_id":"effect_explosion"
            });
            this.self.updateAttackBoxStats(2, {
                "hasEffect":true,
                "damage":26,
                "hitStun":6,
                "selfHitStun":6,
                "direction":30,
                "power":90,
                "kbConstant":100,
                "effectSound":"brawl_bomb_l",
                "effect_id":"effect_explosion"
            });
            this.self.refreshAttackID();
        }

        internal function frame56():*
        {
            this.self.removeFromCamera();
        }

        internal function frame98():*
        {
            this.self.destroy();
        }


    }
}

