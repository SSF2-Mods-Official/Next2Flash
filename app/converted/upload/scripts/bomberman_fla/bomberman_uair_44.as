package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_uair_44 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_uair_44()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 15, this.frame16, 18, this.frame19, 19, this.frame20, 23, this.frame24);
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
            this.self.attachEffect("global_spark", {"y":-50});
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_uair", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame16():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
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

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

