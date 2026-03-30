package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Shield_89 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function Shield_89()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 9, this.frame10);
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

        internal function frame4():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame5():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame10():*
        {
            this.self.endAttack();
        }


    }
}

