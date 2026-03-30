package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class HangRoll_98 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function HangRoll_98()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 8, this.frame9, 18, this.frame19, 21, this.frame22, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame3():*
        {
            this.self.playSound("bandanadee_jump1");
        }

        internal function frame9():*
        {
            this.self.playSound("bandanadee_dashstart");
        }

        internal function frame19():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame22():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("bandanadee_land1");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

