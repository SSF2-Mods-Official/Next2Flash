package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_bair_46 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_bair_46()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 11, this.frame12, 13, this.frame14, 14, this.frame15, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame4():*
        {
            this.self.setLandingLag(true);
            this.self.playAttackSound(1);
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(-30),
                "y":-17,
                "parentLock":true
            });
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_bair", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame12():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }

        internal function frame15():*
        {
            this.self.removeAllEffects();
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }


    }
}

