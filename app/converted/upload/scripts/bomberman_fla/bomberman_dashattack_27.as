package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_dashattack_27 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_dashattack_27()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 6, this.frame7, 11, this.frame12, 15, this.frame16, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(15),
                "scaleX":0.75,
                "scaleY":0.4
            });
        }

        internal function frame7():*
        {
            this.self.setXSpeed(23, false);
            this.self.playAttackSound(1);
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_dash", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame12():*
        {
            this.self.setXSpeed(0);
            this.self.playSound("bomberman_turn");
            this.self.attachEffect("global_dust_cloud");
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame16():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

