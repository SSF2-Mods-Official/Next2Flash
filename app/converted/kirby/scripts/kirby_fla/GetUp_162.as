package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class GetUp_162 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var ready:*;

        public function GetUp_162()
        {
            super();
            addFrameScript(0, this.frame1, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 25, this.frame26, 30, this.frame31, 35, this.frame36, 36, this.frame37, 46, this.frame47, 49, this.frame50);
        }

        public function standCountdown(_arg_1:*=null):*
        {
            if (this.self.getGlobalVariable("standtime") > 0)
            {
                this.self.setGlobalVariable("standtime", (this.self.getGlobalVariable("standtime") - 1));
            }
            else
            {
                this.self.destroyTimer(this.standCountdown);
                gotoAndStop("collapse");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.ready = false;
                this.self.setGlobalVariable("canStartRise", true);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("kirby_land2");
                };
            };
        }

        internal function frame13():*
        {
            this.self.attachEffect("effect_land");
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("canStartRise", true);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_s");
                }
                else
                {
                    this.self.playSound("kirby_land1");
                };
            };
        }

        internal function frame14():*
        {
            stop();
            this.ready = true;
        }

        internal function frame15():*
        {
            this.self.stancePlayFrame("dead");
        }

        internal function frame16():*
        {
            if (!this.self.isForcedCrash())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame26():*
        {
            if (!this.self.isForcedCrash())
            {
                this.self.setIntangibility(false);
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }

        internal function frame36():*
        {
            if (this.self.getGlobalVariable("standloop") > 0)
            {
                gotoAndStop("standloop");
            };
        }

        internal function frame37():*
        {
            if (this.self.getGlobalVariable("standtime") > 0)
            {
                gotoAndStop("standloop");
                this.self.createTimer(1, -1, this.standCountdown);
            };
        }

        internal function frame47():*
        {
            this.self.setGlobalVariable("canStartRise", true);
            this.self.attachEffect("effect_land");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        internal function frame50():*
        {
            if (this.self.getState() == CState.CRASH_GETUP)
            {
                this.self.setState(CState.CRASH_LAND);
            };
            gotoAndStop("dead");
        }


    }
}

