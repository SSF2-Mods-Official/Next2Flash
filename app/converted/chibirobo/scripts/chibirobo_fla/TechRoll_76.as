package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class TechRoll_76 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function TechRoll_76()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 20, this.frame21);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
                this.self.setGlobalVariable("canStartRise", true);
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("chibi_pickplug", true);
                };
            };
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }


    }
}

