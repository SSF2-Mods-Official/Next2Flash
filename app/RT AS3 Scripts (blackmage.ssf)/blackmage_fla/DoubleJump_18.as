// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.DoubleJump_18

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class DoubleJump_18 extends MovieClip 
    {

        internal var hand:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;
        internal var done:Boolean;
        internal var xframe:*;

        public function DoubleJump_18()
        {
            addFrameScript(0, this.frame1, 7, this.frame8, 15, this.frame16);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:BlackMageExt;
            var _local_7:Boolean;
            var _local_8:*;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.done = false;
                this.xframe = "midair";
                if (((this.self.getGlobalVariable("screwAttackOn")) && (this.self.getMidairJumpCount() < 2)))
                {
                    this.self.forceAttack("item_screw");
                }
                else
                {
                    if (((this.self.getGlobalVariable("sonicShieldFiredash")) && ((this.self.getControls().LEFT) || (this.self.getControls().RIGHT))))
                    {
                        this.self.forceAttack("item_firedash");
                    }
                    else
                    {
                        if (((this.self.getGlobalVariable("sonicShieldBubbleBounce")) && (this.self.getControls().DOWN)))
                        {
                            this.self.forceAttack("item_bubblebounce");
                        }
                        else
                        {
                            if ((((this.self.isFacingRight()) && (this.self.getControls().LEFT)) || ((!(this.self.isFacingRight())) && (this.self.getControls().RIGHT))))
                            {
                                this.self.stancePlayFrame("backflip");
                            };
                        };
                    };
                };
            };
        }

        internal function frame8():*
        {
            this.self.endAttack();
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

