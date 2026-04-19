package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class DTilt_105 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function DTilt_105()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 5, this.frame6, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.attachEffect("global_spark");
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.setXSpeed(3, false);
            this.self.playSound("bm_knife");
        }

        internal function frame4():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_bmage_dtilt", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame6():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(30),
                "y":-2,
                "parentLock":true
            });
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

