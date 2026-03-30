package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class FSmash_25 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var self:SimonExt;
        public var xframe:String;

        public function FSmash_25()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 46, this.frame47, 47, this.frame48, 55, this.frame56, 69, this.frame70);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            this.xframe = null;
        }

        internal function frame7():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame47():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame48():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame56():*
        {
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame70():*
        {
            this.self.endAttack();
        }


    }
}

