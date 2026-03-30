package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Getup_84 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var ready:*;

        public function Getup_84()
        {
            super();
            addFrameScript(0, this.frame1, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 26, this.frame27, 30, this.frame31, 35, this.frame36, 36, this.frame37, 46, this.frame47, 49, this.frame50);
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
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            SSF2API.getCamera().shake(3);
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
                    this.self.playSound("chibi_EStep");
                };
            };
        }

        internal function frame13():*
        {
            this.self.attachEffect("effect_land");
            this.ready = true;
            SSF2API.getCamera().shake(1);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_s");
                }
                else
                {
                    this.self.playSound("chibi_DStep");
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

        internal function frame27():*
        {
            this.self.setIntangibility(false);
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
            this.self.attachEffect("effect_land");
            SSF2API.getCamera().shake(1);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("chibi_DStep");
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

