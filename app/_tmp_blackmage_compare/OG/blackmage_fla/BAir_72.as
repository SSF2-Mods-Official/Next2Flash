package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class BAir_72 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function BAir_72()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 5, this.frame6, 12, this.frame13, 16, this.frame17, 17, this.frame18, 22, this.frame23);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
                this.self.attachEffect("global_spark", {
                    "x":this.self.flipX(6),
                    "y":-25
                });
            };
        }

        internal function frame2():*
        {
            this.self.playSound("bm_knife");
            this.self.setLandingLag(true);
            this.self.addEffectToList(this.self.attachEffect("trail_bmage_bair", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(-35),
                "y":-4,
                "parentLock":true
            });
        }

        internal function frame6():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "direction":125,
                "hitStun":3,
                "selfHitStun":1
            });
        }

        internal function frame13():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }

        internal function frame18():*
        {
            this.self.updateAttackStats({"cancelWhenAirborne":true});
            this.self.removeAllEffects();
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("blackmage_landLight");
            };
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }


    }
}

