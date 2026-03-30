package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Taunts_110 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Taunts_110()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 19, this.frame20, 40, this.frame41, 41, this.frame42, 73, this.frame74, 74, this.frame75, 82, this.frame83, 86, this.frame87, 90, this.frame91, 106, this.frame107);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame2():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            };
        }

        internal function frame20():*
        {
            this.self.playSound("gw_entrance3");
        }

        internal function frame41():*
        {
            this.self.endAttack();
        }

        internal function frame42():*
        {
            this.self.playSound("gw_taunt");
        }

        internal function frame74():*
        {
            this.self.endAttack();
        }

        internal function frame75():*
        {
            this.self.playSound("beep_low");
        }

        internal function frame83():*
        {
            this.self.playSound("gw_step1");
        }

        internal function frame87():*
        {
            this.self.playSound("beep_low");
        }

        internal function frame91():*
        {
            this.self.playSound("beep_nair");
        }

        internal function frame107():*
        {
            this.self.endAttack();
        }


    }
}

