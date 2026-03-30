package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class EdgeLean_98 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function EdgeLean_98()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 6, this.frame7, 8, this.frame9, 22, this.frame23, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame3():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame7():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame9():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame23():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame25():*
        {
            this.self.updateAuraPaws();
        }


    }
}

