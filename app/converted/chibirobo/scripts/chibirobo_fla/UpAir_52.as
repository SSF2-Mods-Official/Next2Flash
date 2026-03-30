package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class UpAir_52 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function UpAir_52()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 5, this.frame6, 6, this.frame7, 12, this.frame13, 20, this.frame21, 21, this.frame22, 28, this.frame29);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.attachEffect("global_spark", {"y":-22});
                this.self.setLandingLag(false);
            };
        }

        internal function frame4():*
        {
            this.self.playSound("whoosh1");
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(55),
                "y":-50
            });
            this.self.setLandingLag(true);
        }

        internal function frame6():*
        {
        }

        internal function frame7():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "power":50,
                "kbConstant":65,
                "direction":60,
                "effectSound":"brawl_zap_s",
                "hitStun":2,
                "selfHitStun":1,
                "hitLag":-1.1
            });
        }

        internal function frame13():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
        {
            SSF2API.print("continue");
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("chibi_DStep");
            };
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }


    }
}

