package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class TechRoll_105 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function TechRoll_105()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 15, this.frame16, 20, this.frame21);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
                this.self.setGlobalVariable("canStartRise", true);
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("lucario_tech", true);
                };
            };
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame16():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }


    }
}

