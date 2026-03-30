package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeRoll_87 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function LedgeRoll_87()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 7, this.frame8, 8, this.frame9, 18, this.frame19, 19, this.frame20, 24, this.frame25);
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

        internal function frame8():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame9():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame19():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame20():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

