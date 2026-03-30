package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeGetup_86 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function LedgeGetup_86()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 8, this.frame9, 14, this.frame15, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
                this.self.updateAuraPaws();
            };
        }

        internal function frame3():*
        {
            this.self.updateAuraPaws();
            this.self.playSound("lucario_jump1");
        }

        internal function frame9():*
        {
            this.self.setXSpeed(6.5, false);
        }

        internal function frame15():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}

