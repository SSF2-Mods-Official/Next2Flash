// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Idle_3

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Idle_3 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;
        internal var used:Boolean;
        internal var rand:int;
        internal var repeats:int;

        public function Idle_3()
        {
            addFrameScript(0, this.frame1, 11, this.frame12, 35, this.frame36, 65, this.frame66, 69, this.frame70);
        }

        public function restoreSpecials():*
        {
            this.self.setAttackEnabled(true, "b_forward");
            this.self.setAttackEnabled(true, "b_forward_air");
        }

        public function uncrouch(_arg_1:*=null):*
        {
            if (((_arg_1.data.fromState == 12) && (this.self.getGlobalVariable("crouchdown"))))
            {
                this.self.setGlobalVariable("crouchdown", false);
                this.self.stancePlayFrame("uncrouch");
            }
            else
            {
                this.self.setGlobalVariable("crouchdown", false);
            };
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:BlackMageExt;
            var _local_5:Boolean;
            var _local_6:int;
            var _local_7:int;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            this.used = false;
            this.rand = 0;
            if (!this.repeats)
            {
                this.repeats = 0;
            };
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                this.rand = (100 * SSF2API.random());
                if (this.rand >= 95)
                {
                    this.gotoAndStop("bored");
                }
                else
                {
                    if (this.rand >= 85)
                    {
                        this.gotoAndStop("blink");
                    };
                };
            };
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.restoreSpecials();
            };
            if ((((this.self) && (SSF2API.isReady())) && (!(this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch)))))
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
            };
        }

        internal function frame12():*
        {
            this.repeats++;
            this.gotoAndStop("loop");
        }

        internal function frame36():*
        {
            this.repeats++;
            this.gotoAndStop("loop");
        }

        internal function frame66():*
        {
            this.gotoAndStop("loop");
        }

        internal function frame70():*
        {
            gotoAndStop("loop");
        }


    }
}//package blackmage_fla

