package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class DashAttack_29 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function DashAttack_29()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 8, this.frame9, 9, this.frame10, 14, this.frame15, 15, this.frame16, 21, this.frame22);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame3():*
        {
            this.self.setXSpeed(25, false);
            this.self.playSound("gw_dashattack01");
            this.self.playSound("gw_dashattack02");
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame4():*
        {
            this.self.setXSpeed(0, false);
        }

        internal function frame9():*
        {
            this.self.setXSpeed(35, false);
        }

        internal function frame10():*
        {
            this.self.setXSpeed(0, false);
        }

        internal function frame15():*
        {
            this.self.setXSpeed(30, false);
        }

        internal function frame16():*
        {
            this.self.setXSpeed(0, false);
        }

        internal function frame22():*
        {
            this.self.endAttack();
        }


    }
}

