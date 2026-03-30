package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class USmash_28 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var xframe:String;
        public var hit2:*;

        public function USmash_28()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 42, this.frame43, 43, this.frame44, 53, this.frame54, 55, this.frame56, 60, this.frame61, 61, this.frame62, 74, this.frame75);
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
            this.hit2 = {
                "canDI":true,
                "direction":110,
                "damage":9,
                "power":70,
                "weightKB":0,
                "kbConstant":90
            };
        }

        internal function frame3():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame43():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame44():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame54():*
        {
            this.self.playAttackSound(2);
            this.self.playVoiceSound(1);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame56():*
        {
            this.self.updateAttackBoxStats(1, {"direction":250});
        }

        internal function frame61():*
        {
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, this.hit2);
            this.self.updateAttackBoxStats(2, this.hit2);
        }

        internal function frame62():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame75():*
        {
            this.self.endAttack();
        }


    }
}

