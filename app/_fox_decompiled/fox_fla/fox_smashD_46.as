package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_smashD_46 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var attackBox4:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var xframe:String;

        public function fox_smashD_46()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 41, this.frame42, 42, this.frame43, 43, this.frame44, 64, this.frame65);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(8),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
        }

        internal function frame2():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame42():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame43():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame44():*
        {
            this.self.playVoiceSound(1);
            this.self.playAttackSound(1);
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame65():*
        {
            this.self.endAttack();
        }


    }
}

