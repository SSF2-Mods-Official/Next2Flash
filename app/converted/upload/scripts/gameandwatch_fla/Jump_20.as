package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Jump_20 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var xframe:*;
        public var done:*;
        public var firstTimeHere:Boolean;

        public function Jump_20()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 20, this.frame21, 21, this.frame22, 39, this.frame40);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            this.xframe = "midair";
            this.done = false;
            this.firstTimeHere = true;
            if (parent && SSF2API.isReady() && this.self && this.self.getGlobalVariable("screwAttackOn"))
            {
                this.self.endAttack();
                this.self.forceAttack("item_screw");
            };
        }

        internal function frame2():*
        {
            this.self.playSound("gw_jump1");
        }

        internal function frame3():*
        {
            if (this.firstTimeHere)
            {
                this.firstTimeHere = false;
            }
            else
            {
                SSF2API.print("jump frame");
            };
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
        {
            SSF2API.print("backflip frame");
        }

        internal function frame40():*
        {
            this.self.endAttack();
        }


    }
}

