package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class HangRoll_77 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function HangRoll_77()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 8, this.frame9, 18, this.frame19, 19, this.frame20, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            SSF2API.playSound("simon_dashstart");
        }

        internal function frame9():*
        {
            SSF2API.playSound("simon_dashstart");
        }

        internal function frame19():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("simon_land_heavy");
            };
        }

        internal function frame20():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

