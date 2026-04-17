package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_jump_29 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var xframe:*;
        public var done:*;

        public function fox_jump_29()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            this.xframe = "midair";
            this.done = false;
            if (SSF2API.isReady() && this.self && this.self.getGlobalVariable("screwAttackOn"))
            {
                this.self.endAttack();
                this.self.forceAttack("item_screw");
            };
        }

        internal function frame2():*
        {
            this.self.playSound("fox_jump01");
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

